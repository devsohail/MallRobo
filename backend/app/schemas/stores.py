import uuid

from pydantic import BaseModel


class StoreResponse(BaseModel):
    id: uuid.UUID
    name: str

    model_config = {"from_attributes": True}
