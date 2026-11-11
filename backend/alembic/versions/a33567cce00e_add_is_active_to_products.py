"""add is_active to products

Revision ID: a33567cce00e
Revises: 6ae6642e0d28
Create Date: 2026-08-03 16:58:13.946680

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a33567cce00e"
down_revision: Union[str, Sequence[str], None] = "6ae6642e0d28"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # =====================================================
    # PRODUCTS
    # =====================================================

    op.add_column(
        "products",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true")
        )
    )

    op.alter_column(
        "products",
        "is_active",
        server_default=None
    )

    # =====================================================
    # PURCHASE INVOICE ITEMS
    # =====================================================

    op.alter_column(
        "purchase_invoice_items",
        "warehouse_id",
        existing_type=sa.INTEGER(),
        nullable=False
    )

    op.alter_column(
        "purchase_invoice_items",
        "unit_id",
        existing_type=sa.INTEGER(),
        nullable=False
    )

    # =====================================================
    # PURCHASE ORDER ITEMS
    # =====================================================

    op.add_column(
        "purchase_order_items",
        sa.Column(
            "hsn_code",
            sa.String(length=30),
            nullable=True
        )
    )

    op.add_column(
        "purchase_order_items",
        sa.Column(
            "serial_number",
            sa.String(length=200),
            nullable=True
        )
    )

    # Create indexes only if they don't already exist
    op.execute("""
    CREATE INDEX IF NOT EXISTS ix_purchase_order_items_unit_id
    ON purchase_order_items(unit_id);
    """)

    op.execute("""
    CREATE INDEX IF NOT EXISTS ix_purchase_order_items_warehouse_id
    ON purchase_order_items(warehouse_id);
    """)


def downgrade() -> None:
    """Downgrade schema."""

    op.execute("""
    DROP INDEX IF EXISTS ix_purchase_order_items_warehouse_id;
    """)

    op.execute("""
    DROP INDEX IF EXISTS ix_purchase_order_items_unit_id;
    """)

    op.drop_column(
        "purchase_order_items",
        "serial_number"
    )

    op.drop_column(
        "purchase_order_items",
        "hsn_code"
    )

    op.alter_column(
        "purchase_invoice_items",
        "unit_id",
        existing_type=sa.INTEGER(),
        nullable=True
    )

    op.alter_column(
        "purchase_invoice_items",
        "warehouse_id",
        existing_type=sa.INTEGER(),
        nullable=True
    )

    op.drop_column(
        "products",
        "is_active"
    )