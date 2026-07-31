import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Product, Store
from app.schemas import ProductResponse, StoreResponse

router = APIRouter(prefix="/api/stores", tags=["stores"])


@router.get("", response_model=list[StoreResponse])
async def get_stores(db: AsyncSession = Depends(get_db)) -> list[StoreResponse]:
    result = await db.execute(select(Store).order_by(Store.name))
    stores = result.scalars().all()
    return [StoreResponse.model_validate(s) for s in stores]


@router.get("/{store_id}/products", response_model=list[ProductResponse])
async def get_store_products(
    store_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[ProductResponse]:
    store = await db.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    result = await db.execute(
        select(Product).where(Product.store_id == store_id).order_by(Product.name)
    )
    products = result.scalars().all()
    return [ProductResponse.model_validate(p) for p in products]
