from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.pathfinding.solver import UnreachableProductError
from app.schemas import Point, RouteRequest, RouteResponse
from app.services.route_service import ProductNotFoundError, compute_route_for_products

router = APIRouter(prefix="/api", tags=["route"])


@router.post("/route", response_model=RouteResponse)
async def calculate_route(
    body: RouteRequest,
    db: AsyncSession = Depends(get_db),
) -> RouteResponse | JSONResponse:
    try:
        route_result, total_price = await compute_route_for_products(db, body.product_ids)
    except ProductNotFoundError as e:
        return JSONResponse(
            status_code=404,
            content={
                "detail": "Products not found",
                "product_ids": [str(pid) for pid in e.missing_ids],
            },
        )
    except UnreachableProductError as e:
        return JSONResponse(
            status_code=409,
            content={
                "detail": "Unreachable products",
                "unreachable_points": [
                    {"x": p[0], "y": p[1]} for p in e.unreachable_points
                ],
            },
        )

    return RouteResponse(
        visit_order=[Point(x=p[0], y=p[1]) for p in route_result.visit_order],
        cells=[Point(x=p[0], y=p[1]) for p in route_result.cells],
        total_seconds=route_result.total_seconds,
        total_price=total_price,
        exact=route_result.exact,
    )
