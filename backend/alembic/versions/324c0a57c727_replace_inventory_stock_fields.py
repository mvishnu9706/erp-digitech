"""replace inventory stock fields

Revision ID: 324c0a57c727
Revises: 5e5478e65105
Create Date: 2026-08-18

"""

from alembic import op
import sqlalchemy as sa


# =========================================================
# Revision identifiers
# =========================================================

revision = "324c0a57c727"

down_revision = "5e5478e65105"

branch_labels = None

depends_on = None


# =========================================================
# Upgrade
# =========================================================

def upgrade():

    # =====================================================
    # 1. Add the new stock column
    #
    # Initially nullable so existing inventory rows can be
    # populated from current_stock.
    # =====================================================

    op.add_column(
        "inventory",
        sa.Column(
            "stock",
            sa.Integer(),
            nullable=True,
        ),
    )

    # =====================================================
    # 2. Copy existing current_stock into stock
    #
    # IMPORTANT:
    #
    # Existing stock data is preserved.
    #
    # Example:
    #
    # current_stock  = 50
    # reserved_stock = 10
    # available_stock = 40
    #
    # New system:
    #
    # stock = 50
    #
    # We intentionally use current_stock because the new
    # inventory system maintains only actual physical stock.
    # =====================================================

    op.execute(
        """
        UPDATE inventory
        SET stock = COALESCE(current_stock, 0)
        """
    )

    # =====================================================
    # 3. Make stock NOT NULL
    # =====================================================

    op.alter_column(
        "inventory",
        "stock",
        existing_type=sa.Integer(),
        nullable=False,
        server_default="0",
    )

    # =====================================================
    # 4. Remove current_stock
    # =====================================================

    op.drop_column(
        "inventory",
        "current_stock",
    )

    # =====================================================
    # 5. Remove reserved_stock
    # =====================================================

    op.drop_column(
        "inventory",
        "reserved_stock",
    )

    # =====================================================
    # 6. Remove available_stock
    # =====================================================

    op.drop_column(
        "inventory",
        "available_stock",
    )

    # =====================================================
    # 7. Remove reserved_quantity from sales_order_items
    #
    # Sales orders no longer reserve inventory.
    #
    # Stock is deducted only when the sales order is
    # successfully completed.
    # =====================================================

    op.drop_column(
        "sales_order_items",
        "reserved_quantity",
    )


# =========================================================
# Downgrade
# =========================================================

def downgrade():

    # =====================================================
    # 1. Recreate current_stock
    # =====================================================

    op.add_column(
        "inventory",
        sa.Column(
            "current_stock",
            sa.Integer(),
            nullable=True,
        ),
    )

    # =====================================================
    # 2. Recreate reserved_stock
    # =====================================================

    op.add_column(
        "inventory",
        sa.Column(
            "reserved_stock",
            sa.Integer(),
            nullable=True,
        ),
    )

    # =====================================================
    # 3. Recreate available_stock
    # =====================================================

    op.add_column(
        "inventory",
        sa.Column(
            "available_stock",
            sa.Integer(),
            nullable=True,
        ),
    )

    # =====================================================
    # 4. Restore current_stock from stock
    #
    # The new system only stores one stock quantity.
    # Therefore current_stock receives the stock value.
    # =====================================================

    op.execute(
        """
        UPDATE inventory
        SET current_stock = COALESCE(stock, 0)
        """
    )

    # =====================================================
    # 5. Restore reserved_stock
    #
    # Reservation information cannot be reconstructed
    # because it was intentionally removed.
    #
    # Therefore it is restored as zero.
    # =====================================================

    op.execute(
        """
        UPDATE inventory
        SET reserved_stock = 0
        """
    )

    # =====================================================
    # 6. Restore available_stock
    #
    # With no reservation information available,
    # available_stock is restored equal to current_stock.
    # =====================================================

    op.execute(
        """
        UPDATE inventory
        SET available_stock = COALESCE(current_stock, 0)
        """
    )

    # =====================================================
    # 7. Make current_stock NOT NULL
    # =====================================================

    op.alter_column(
        "inventory",
        "current_stock",
        existing_type=sa.Integer(),
        nullable=False,
        server_default="0",
    )

    # =====================================================
    # 8. Make reserved_stock NOT NULL
    # =====================================================

    op.alter_column(
        "inventory",
        "reserved_stock",
        existing_type=sa.Integer(),
        nullable=False,
        server_default="0",
    )

    # =====================================================
    # 9. Make available_stock NOT NULL
    # =====================================================

    op.alter_column(
        "inventory",
        "available_stock",
        existing_type=sa.Integer(),
        nullable=False,
        server_default="0",
    )

    # =====================================================
    # 10. Remove new stock column
    # =====================================================

    op.drop_column(
        "inventory",
        "stock",
    )

    # =====================================================
    # 11. Recreate reserved_quantity
    # =====================================================

    op.add_column(
        "sales_order_items",
        sa.Column(
            "reserved_quantity",
            sa.Integer(),
            nullable=True,
            server_default="0",
        ),
    )

    # =====================================================
    # 12. Populate reserved_quantity with zero
    # =====================================================

    op.execute(
        """
        UPDATE sales_order_items
        SET reserved_quantity = 0
        """
    )

    # =====================================================
    # 13. Make reserved_quantity NOT NULL
    # =====================================================

    op.alter_column(
        "sales_order_items",
        "reserved_quantity",
        existing_type=sa.Integer(),
        nullable=False,
        server_default="0",
    )