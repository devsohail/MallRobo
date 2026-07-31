"""Initial schema: grid, stores, products

Revision ID: 001
Revises:
Create Date: 2024-01-01

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "grid",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("x", sa.Integer(), nullable=False),
        sa.Column("y", sa.Integer(), nullable=False),
        sa.Column("path", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("robot_start", sa.Boolean(), nullable=False, server_default="false"),
        sa.UniqueConstraint("x", "y", name="uq_grid_xy"),
    )
    # Partial unique index to enforce at most one robot_start
    op.create_index(
        "ix_grid_single_robot_start",
        "grid",
        ["robot_start"],
        unique=True,
        postgresql_where=sa.text("robot_start = true"),
    )

    op.create_table(
        "stores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
    )

    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("x", sa.Integer(), nullable=False),
        sa.Column("y", sa.Integer(), nullable=False),
        sa.Column(
            "store_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("stores.id"),
            nullable=False,
        ),
        sa.CheckConstraint("price > 0", name="ck_products_price_positive"),
    )


def downgrade() -> None:
    op.drop_table("products")
    op.drop_table("stores")
    op.drop_index("ix_grid_single_robot_start", table_name="grid")
    op.drop_table("grid")
