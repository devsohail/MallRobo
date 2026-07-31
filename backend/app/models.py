import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Uuid, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class GridCell(Base):
    __tablename__ = "grid"
    __table_args__ = (
        UniqueConstraint("x", "y", name="uq_grid_xy"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid.uuid4
    )
    x: Mapped[int] = mapped_column(Integer, nullable=False)
    y: Mapped[int] = mapped_column(Integer, nullable=False)
    path: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    robot_start: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    products: Mapped[list["Product"]] = relationship(back_populates="store")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    x: Mapped[int] = mapped_column(Integer, nullable=False)
    y: Mapped[int] = mapped_column(Integer, nullable=False)
    store_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("stores.id"), nullable=False
    )
    store: Mapped["Store"] = relationship(back_populates="products")
