import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class Point(BaseModel):
    x: int
    y: int


class RouteRequest(BaseModel):
    product_ids: list[uuid.UUID] = Field(..., max_length=50)


class RouteResponse(BaseModel):
    visit_order: list[Point]
    cells: list[Point]
    total_seconds: int
    total_price: Decimal
    exact: bool
