# AI Review Log

This document tracks instances where AI-generated code was corrected during development.

| # | Date | What Was Wrong | How Found | Fix Applied |
|---|------|---------------|-----------|-------------|
| 1 | 2026-07-31 | `product.price` treated as `number` but API returns it as `string` (Decimal serialization). Caused `TypeError: price.toFixed is not a function` in `ProductList.tsx` and `Cart.tsx`. | User reported runtime crash when selecting a store and adding products to cart. | Wrapped all `price` usages with `Number()` before calling `.toFixed(2)` or arithmetic in `ProductList.tsx:43` and `Cart.tsx:15,29`. |
| 2 | 2026-08-01 | Pathfinding algorithm choice questioned — BFS + TSP was used instead of BFS + A\*. | Human code review. | No change needed. BFS is optimal for unweighted grids (O(1) queue ops vs A\*'s O(log n) priority queue). A\* heuristic adds overhead with zero benefit on uniform-cost grids. TSP is a separate concern — it solves visit-order optimization (N! orderings), which BFS cannot address. See detailed analysis below. |
| 3 | 2026-08-01 | `Product.id.in_(list[uuid.UUID])` returned empty results on Railway's PostgreSQL + asyncpg, causing route endpoint to 404 for valid product IDs. | Human reported 404 on production `/api/route` with valid IDs confirmed via `/api/stores/{id}/products`. | Replaced `IN` clause with `or_(*[Product.id == pid for pid in unique_ids])`. Individual equality conditions bind correctly with asyncpg. See `backend/app/services/route_service.py:58-60`. |
| 4 | 2026-08-01 | No pre-commit hook existed — tests were not enforced before commits. AI commits bypassed testing gate via `--no-verify` or simply because no hook was configured. | Human committed a file and noticed tests did not run. | Created `scripts/pre-commit` hook that runs backend pytest and frontend vitest before each commit, aborting on failure. Added `scripts/install-hooks.sh` for portable setup. |

---

## Review 2 — Pathfinding Algorithm Choice (2026-08-01)

**Reviewer:** Sohail Sajid (Human)
**Status:** Resolved — no code change required

### Issue: BFS + A* vs BFS + TSP

The initial implementation was questioned for not using A* alongside BFS for pathfinding. After review, the following was established:

**Why BFS, not A\*:**

- The mall grid is **unweighted** — every step between adjacent cells costs exactly 1 unit. BFS guarantees shortest paths on unweighted graphs with O(V + E) time using a simple FIFO queue (O(1) per operation).
- A\* adds a priority queue (O(log n) per insertion) and heuristic computation overhead that provides **zero benefit** on a uniform-cost grid. BFS already expands nodes in optimal order.
- The system needs **all-pairs shortest distances** (via `bfs_distance_matrix`), not single source-to-target queries. BFS from one source gives distances to all reachable cells in a single pass. A\* would need to be invoked separately for each pair.

**Why TSP is required (separate concern from BFS):**

- BFS answers: "What is the shortest path between two specific points?"
- TSP answers: "In what order should the robot visit N product locations to minimize total travel?"
- With N products there are N! possible visit orderings. BFS cannot determine the optimal ordering — that is a combinatorial optimization problem (Travelling Salesman Problem).
- The implementation uses **Held-Karp** (exact, O(2^k · k²)) for ≤12 waypoints and **Nearest-Neighbor + 2-opt** (heuristic) for >12 waypoints.

**Conclusion:** BFS + TSP is the correct two-phase architecture. BFS handles grid-level shortest paths; TSP handles visit-order optimization. A\* would be appropriate only if the grid had variable movement costs (e.g., different terrain types).

---

## Review 3 — asyncpg UUID IN Clause Bug (2026-08-01)

**Reviewer:** Sohail Sajid (Human)
**Status:** Resolved

### Symptom
`POST /api/route` returned `{"detail":"Products not found"}` with product IDs that existed and were returned correctly by `GET /api/stores/{id}/products`. Occurred on Railway's PostgreSQL + asyncpg deployment. Local development also uses PostgreSQL via Docker Compose; the test suite uses in-memory SQLite (aiosqlite) per `tests/conftest.py`.

### Root Cause
`asyncpg` has a known issue binding a Python `list[uuid.UUID]` as a PostgreSQL UUID array parameter in SQLAlchemy `IN` clauses:

```python
# BROKEN with asyncpg + PostgreSQL
result = await db.execute(select(Product).where(Product.id.in_(unique_ids)))
```

The stores endpoint worked because it uses a single equality comparison (`Product.store_id == store_id`), which binds correctly.

### Fix
Replaced `IN` clause with individual `OR` equality conditions (`route_service.py:58-60`):

```python
conditions = [Product.id == pid for pid in unique_ids]
result = await db.execute(select(Product).where(or_(*conditions)))
```

### Verification
- All 42 backend tests pass (test suite uses in-memory SQLite via aiosqlite)
- Local Docker Compose app runs correctly (PostgreSQL 16 + asyncpg)
- Production route endpoint works correctly on Railway (PostgreSQL + asyncpg)
- The `product_ids` cap of 50 in `RouteRequest` schema keeps the OR chain bounded

### Alternatives considered and rejected
- `cast(pid, PG_UUID(as_uuid=True))` — PostgreSQL-specific, broke test suite (which runs on SQLite)
- Converting UUIDs to strings — would require model-layer changes

---

## Review 4 — Missing Pre-commit Hook (2026-08-01)

**Reviewer:** Sohail Sajid (Human)
**Status:** Resolved

### Issue
No git pre-commit hook was configured. The project's `CLAUDE.md` mandates "Tests must pass before any commit," but nothing enforced this. Commits could land without running the test suite.

### How Found
Human manually edited and committed a file — no tests ran.

### Fix
- Created `scripts/pre-commit` — runs `python -m pytest tests/ -q` (backend) and `npx vitest run` (frontend), aborting the commit if either fails.
- Created `scripts/install-hooks.sh` — copies the hook to `.git/hooks/pre-commit` (since `.git/hooks/` is not tracked by git).
- Updated `README.md` with setup instructions.

### Verification
- Committed with the hook active — all 42 backend and 39 frontend tests ran and passed before the commit was accepted.
