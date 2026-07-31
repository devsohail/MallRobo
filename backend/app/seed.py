"""Seed the database with the PDF's 14x9 example grid, stores, and products."""

import asyncio
import uuid

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models import GridCell, Product, Store

# 14x9 grid layout (0-indexed)
# 1 = path, 0 = obstacle, S = robot start (also path)
# Row 0 is top
GRID_LAYOUT = [
    # x: 0  1  2  3  4  5  6  7  8  9 10 11 12 13
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # y=0
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],  # y=1
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],  # y=2
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # y=3
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],  # y=4
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],  # y=5
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # y=6
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # y=7
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # y=8
]

ROBOT_START = (0, 0)

# Store and product definitions
STORES_DATA = [
    {
        "name": "Electronics Hub",
        "products": [
            {"name": "Wireless Earbuds", "price": 29.99, "x": 3, "y": 0},
            {"name": "Phone Charger", "price": 14.99, "x": 6, "y": 0},
            {"name": "USB Cable", "price": 9.99, "x": 3, "y": 3},
        ],
    },
    {
        "name": "Fashion Corner",
        "products": [
            {"name": "Sunglasses", "price": 19.99, "x": 9, "y": 0},
            {"name": "Watch Band", "price": 12.99, "x": 9, "y": 3},
            {"name": "Scarf", "price": 15.99, "x": 13, "y": 3},
        ],
    },
    {
        "name": "Book Nook",
        "products": [
            {"name": "Mystery Novel", "price": 8.99, "x": 0, "y": 3},
            {"name": "Cookbook", "price": 22.99, "x": 3, "y": 6},
            {"name": "Travel Guide", "price": 16.99, "x": 6, "y": 6},
        ],
    },
    {
        "name": "Snack Stop",
        "products": [
            {"name": "Chocolate Box", "price": 11.99, "x": 9, "y": 6},
            {"name": "Trail Mix", "price": 6.99, "x": 13, "y": 6},
            {"name": "Energy Bar", "price": 3.99, "x": 0, "y": 6},
        ],
    },
    {
        "name": "Gadget World",
        "products": [
            {"name": "Portable Speaker", "price": 39.99, "x": 0, "y": 8},
            {"name": "LED Keychain", "price": 5.99, "x": 6, "y": 3},
            {"name": "Mini Fan", "price": 7.99, "x": 13, "y": 0},
        ],
    },
]


async def seed_db() -> None:
    async with async_session() as session:
        async with session.begin():
            # Clear existing data
            await session.execute(delete(Product))
            await session.execute(delete(Store))
            await session.execute(delete(GridCell))

            # Seed grid
            for y, row in enumerate(GRID_LAYOUT):
                for x, cell_val in enumerate(row):
                    is_start = (x, y) == ROBOT_START
                    cell = GridCell(
                        id=uuid.uuid4(),
                        x=x,
                        y=y,
                        path=cell_val == 1,
                        robot_start=is_start,
                    )
                    session.add(cell)

            # Seed stores and products
            for store_data in STORES_DATA:
                store = Store(
                    id=uuid.uuid4(),
                    name=store_data["name"],
                )
                session.add(store)

                for prod_data in store_data["products"]:
                    product = Product(
                        id=uuid.uuid4(),
                        name=prod_data["name"],
                        price=prod_data["price"],
                        x=prod_data["x"],
                        y=prod_data["y"],
                        store_id=store.id,
                    )
                    session.add(product)

    print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_db())
