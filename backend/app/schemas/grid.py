from pydantic import BaseModel


class GridCellResponse(BaseModel):
    x: int
    y: int
    path: bool
    robot_start: bool

    model_config = {"from_attributes": True}


class GridResponse(BaseModel):
    width: int
    height: int
    cells: list[GridCellResponse]
