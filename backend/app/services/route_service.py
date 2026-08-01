import uuid
from decimal import Decimal

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GridCell, Product
from app.pathfinding.solver import Point, RouteResult, UnreachableProductError, compute_route


class ProductNotFoundError(Exception):
    def __init__(self, missing_ids: list[uuid.UUID]) -> None:
        self.missing_ids = missing_ids
        super().__init__(f"Products not found: {missing_ids}")


async def load_grid(db: AsyncSession) -> tuple[set[Point], Point]:
    """Load the grid and robot start position from the database."""
    result = await db.execute(select(GridCell))
    cells = result.scalars().all()

    grid: set[Point] = set()
    start: Point | None = None

    for cell in cells:
        if cell.path:
            grid.add((cell.x, cell.y))
        if cell.robot_start:
            start = (cell.x, cell.y)
            grid.add((cell.x, cell.y))  # start is always accessible

    if start is None:
        raise ValueError("No robot_start cell defined in the grid")

    return grid, start


async def compute_route_for_products(
    db: AsyncSession,
    product_ids: list[uuid.UUID],
) -> tuple[RouteResult, Decimal]:
    """Compute route and total price for the given product IDs.

    Returns (RouteResult, total_price).
    Raises ProductNotFoundError or UnreachableProductError.
    """
    grid, start = await load_grid(db)

    # Empty cart
    if not product_ids:
        return (
            RouteResult(visit_order=[], cells=[start], total_seconds=0, exact=True),
            Decimal("0.00"),
        )

    # Fetch products
    unique_ids = list(set(product_ids))
    # Use individual OR conditions to avoid asyncpg UUID array binding issues
    conditions = [Product.id == pid for pid in unique_ids]
    result = await db.execute(select(Product).where(or_(*conditions)))
    products = {p.id: p for p in result.scalars().all()}

    # Check for missing products
    missing = [pid for pid in unique_ids if pid not in products]
    if missing:
        raise ProductNotFoundError(missing)

    # Build product locations (deduplicated by position)
    product_locations: list[Point] = []
    seen_positions: set[Point] = set()
    for pid in unique_ids:
        p = products[pid]
        pos = (p.x, p.y)
        if pos not in seen_positions:
            product_locations.append(pos)
            seen_positions.add(pos)

    # Compute route
    route_result = compute_route(grid, start, product_locations)

    # Calculate total price
    total_price = sum(Decimal(str(products[pid].price)) for pid in unique_ids)

    return route_result, total_price
