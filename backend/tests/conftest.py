"""Shared fixtures for backend tests."""

import uuid
from collections.abc import AsyncGenerator
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_db
from app.main import app
from app.models import Base, GridCell, Product, Store

TEST_DATABASE_URL = "sqlite+aiosqlite://"


@pytest.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create tables, yield a session, then drop tables."""
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    @event.listens_for(test_engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, connection_record):  # type: ignore[no-untyped-def]
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest.fixture()
async def seeded_session(db_session: AsyncSession) -> AsyncSession:
    """Seed a small grid (5x5) with stores and products for API tests."""
    obstacles = {(1, 1), (2, 1), (1, 2), (3, 3)}
    for y in range(5):
        for x in range(5):
            is_path = (x, y) not in obstacles
            is_start = (x, y) == (0, 0)
            db_session.add(GridCell(x=x, y=y, path=is_path, robot_start=is_start))

    store = Store(id=uuid.UUID("00000000-0000-0000-0000-000000000001"), name="Test Store")
    db_session.add(store)
    await db_session.flush()

    products = [
        Product(
            id=uuid.UUID("10000000-0000-0000-0000-000000000001"),
            name="Apple",
            price=Decimal("1.50"),
            x=4,
            y=0,
            store_id=store.id,
        ),
        Product(
            id=uuid.UUID("10000000-0000-0000-0000-000000000002"),
            name="Banana",
            price=Decimal("2.00"),
            x=0,
            y=4,
            store_id=store.id,
        ),
        Product(
            id=uuid.UUID("10000000-0000-0000-0000-000000000003"),
            name="Cherry",
            price=Decimal("3.25"),
            x=4,
            y=4,
            store_id=store.id,
        ),
    ]
    for p in products:
        db_session.add(p)

    await db_session.commit()
    return db_session


@pytest.fixture()
async def client(seeded_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """AsyncClient wired to the FastAPI app with test DB override."""

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield seeded_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
