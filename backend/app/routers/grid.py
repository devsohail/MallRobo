from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import GridCell
from app.schemas import GridCellResponse, GridResponse

router = APIRouter(prefix="/api/grid", tags=["grid"])


@router.get("", response_model=GridResponse)
async def get_grid(db: AsyncSession = Depends(get_db)) -> GridResponse:
    result = await db.execute(select(GridCell).order_by(GridCell.y, GridCell.x))
    cells = result.scalars().all()

    width_result = await db.execute(select(func.max(GridCell.x)))
    height_result = await db.execute(select(func.max(GridCell.y)))
    max_x = width_result.scalar() or 0
    max_y = height_result.scalar() or 0

    return GridResponse(
        width=max_x + 1,
        height=max_y + 1,
        cells=[GridCellResponse.model_validate(c) for c in cells],
    )
