import uuid
from decimal import Decimal

from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: uuid.UUID
    name: str
    price: Decimal
    x: int
    y: int
    store_id: uuid.UUID

    model_config = {"from_attributes": True}
