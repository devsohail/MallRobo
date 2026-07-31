"""API endpoint tests — schema validation, error codes, edge cases."""

import uuid

import pytest
from httpx import AsyncClient

STORE_ID = "00000000-0000-0000-0000-000000000001"
PRODUCT_IDS = [
    "10000000-0000-0000-0000-000000000001",
    "10000000-0000-0000-0000-000000000002",
    "10000000-0000-0000-0000-000000000003",
]


# ── Health ────────────────────────────────────────────────────────────────────

class TestHealth:
    async def test_health(self, client: AsyncClient) -> None:
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


# ── Stores ────────────────────────────────────────────────────────────────────

class TestStores:
    async def test_list_stores_schema(self, client: AsyncClient) -> None:
        resp = await client.get("/api/stores")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 1
        store = data[0]
        assert "id" in store
        assert "name" in store
        assert store["name"] == "Test Store"

    async def test_store_products_schema(self, client: AsyncClient) -> None:
        resp = await client.get(f"/api/stores/{STORE_ID}/products")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 3
        for product in data:
            assert "id" in product
            assert "name" in product
            assert "price" in product
            assert "x" in product
            assert "y" in product
            assert "store_id" in product

    async def test_store_not_found(self, client: AsyncClient) -> None:
        fake_id = str(uuid.uuid4())
        resp = await client.get(f"/api/stores/{fake_id}/products")
        assert resp.status_code == 404
        assert "detail" in resp.json()

    async def test_store_invalid_uuid(self, client: AsyncClient) -> None:
        resp = await client.get("/api/stores/not-a-uuid/products")
        assert resp.status_code == 422


# ── Grid ──────────────────────────────────────────────────────────────────────

class TestGrid:
    async def test_grid_schema(self, client: AsyncClient) -> None:
        resp = await client.get("/api/grid")
        assert resp.status_code == 200
        data = resp.json()
        assert "width" in data
        assert "height" in data
        assert "cells" in data
        assert data["width"] == 5
        assert data["height"] == 5
        assert isinstance(data["cells"], list)

    async def test_grid_cells_have_required_fields(self, client: AsyncClient) -> None:
        resp = await client.get("/api/grid")
        data = resp.json()
        for cell in data["cells"]:
            assert "x" in cell
            assert "y" in cell
            assert "path" in cell
            assert "robot_start" in cell

    async def test_grid_has_robot_start(self, client: AsyncClient) -> None:
        resp = await client.get("/api/grid")
        data = resp.json()
        starts = [c for c in data["cells"] if c["robot_start"]]
        assert len(starts) == 1
        assert starts[0]["x"] == 0
        assert starts[0]["y"] == 0


# ── Route ─────────────────────────────────────────────────────────────────────

class TestRoute:
    async def test_single_product_route(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/route",
            json={"product_ids": [PRODUCT_IDS[0]]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "visit_order" in data
        assert "cells" in data
        assert "total_seconds" in data
        assert "total_price" in data
        assert "exact" in data
        assert data["total_seconds"] > 0
        assert float(data["total_price"]) == 1.50
        assert data["exact"] is True

    async def test_multiple_products_route(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/route",
            json={"product_ids": PRODUCT_IDS},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["visit_order"]) == 3
        assert data["total_seconds"] > 0
        # 1.50 + 2.00 + 3.25 = 6.75
        assert float(data["total_price"]) == pytest.approx(6.75)
        assert data["exact"] is True

    async def test_route_path_continuity(self, client: AsyncClient) -> None:
        """Every consecutive pair in cells must be 4-adjacent."""
        resp = await client.post(
            "/api/route",
            json={"product_ids": PRODUCT_IDS[:2]},
        )
        data = resp.json()
        cells = data["cells"]
        for i in range(len(cells) - 1):
            a, b = cells[i], cells[i + 1]
            dist = abs(a["x"] - b["x"]) + abs(a["y"] - b["y"])
            assert dist == 1, f"Non-adjacent at step {i}: {a} -> {b}"

    async def test_route_starts_and_ends_at_start(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/route",
            json={"product_ids": [PRODUCT_IDS[0]]},
        )
        data = resp.json()
        assert data["cells"][0] == {"x": 0, "y": 0}
        assert data["cells"][-1] == {"x": 0, "y": 0}

    async def test_empty_product_ids_validation(self, client: AsyncClient) -> None:
        """Empty product_ids list should return empty route."""
        resp = await client.post("/api/route", json={"product_ids": []})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_seconds"] == 0
        assert data["cells"] == [{"x": 0, "y": 0}]

    async def test_product_not_found_404(self, client: AsyncClient) -> None:
        fake_id = str(uuid.uuid4())
        resp = await client.post("/api/route", json={"product_ids": [fake_id]})
        assert resp.status_code == 404
        data = resp.json()
        assert "detail" in data
        assert "product_ids" in data

    async def test_malformed_body_422(self, client: AsyncClient) -> None:
        resp = await client.post("/api/route", json={"product_ids": "not-a-list"})
        assert resp.status_code == 422

    async def test_invalid_uuid_in_body_422(self, client: AsyncClient) -> None:
        resp = await client.post("/api/route", json={"product_ids": ["bad-uuid"]})
        assert resp.status_code == 422

    async def test_missing_body_422(self, client: AsyncClient) -> None:
        resp = await client.post("/api/route", content=b"not json")
        assert resp.status_code == 422

    async def test_too_many_products_422(self, client: AsyncClient) -> None:
        """product_ids list exceeding 50 items should be rejected."""
        ids = [str(uuid.uuid4()) for _ in range(51)]
        resp = await client.post("/api/route", json={"product_ids": ids})
        assert resp.status_code == 422

    async def test_duplicate_product_ids(self, client: AsyncClient) -> None:
        """Duplicate IDs should be deduplicated (same route as single)."""
        resp = await client.post(
            "/api/route",
            json={"product_ids": [PRODUCT_IDS[0], PRODUCT_IDS[0]]},
        )
        assert resp.status_code == 200
        data = resp.json()
        # Duplicates are deduplicated — price counted once per unique ID
        assert float(data["total_price"]) == pytest.approx(1.50)
