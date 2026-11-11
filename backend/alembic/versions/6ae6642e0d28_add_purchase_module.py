"""add purchase module

Revision ID: 6ae6642e0d28
Revises: 7b84991261c6
Create Date: 2026-08-03 14:42:11.078940
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision = "6ae6642e0d28"
down_revision = "7b84991261c6"
branch_labels = None
depends_on = None


def upgrade():

    # =====================================================
    # Purchase Invoice
    # =====================================================

    op.drop_index(
        op.f("ix_purchase_invoices_goods_receipt_id"),
        table_name="purchase_invoices",
    )

    op.drop_constraint(
        op.f("purchase_invoices_goods_receipt_id_fkey"),
        "purchase_invoices",
        type_="foreignkey",
    )

    op.drop_column(
        "purchase_invoices",
        "goods_receipt_id",
    )

    # =====================================================
    # Purchase Orders
    # =====================================================

    op.add_column(
        "purchase_orders",
        sa.Column(
            "reference_number",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "purchase_orders",
        sa.Column(
            "currency",
            sa.String(length=10),
            nullable=True,
        ),
    )

    op.add_column(
        "purchase_orders",
        sa.Column(
            "exchange_rate",
            sa.Numeric(12, 4),
            nullable=True,
        ),
    )

    op.add_column(
        "purchase_orders",
        sa.Column(
            "terms_conditions",
            sa.Text(),
            nullable=True,
        ),
    )

    # =====================================================
    # Supplier
    # =====================================================

    op.alter_column(
        "suppliers",
        "supplier_code",
        existing_type=sa.VARCHAR(length=20),
        type_=sa.String(length=30),
        existing_nullable=False,
    )

    op.alter_column(
        "suppliers",
        "company_name",
        existing_type=sa.VARCHAR(length=200),
        type_=sa.String(length=400),
        existing_nullable=False,
    )

    op.alter_column(
        "suppliers",
        "phone",
        existing_type=sa.VARCHAR(length=20),
        type_=sa.String(length=27),
        existing_nullable=True,
    )


def downgrade():

    op.alter_column(
        "suppliers",
        "phone",
        existing_type=sa.String(length=27),
        type_=sa.VARCHAR(length=20),
        existing_nullable=True,
    )

    op.alter_column(
        "suppliers",
        "company_name",
        existing_type=sa.String(length=400),
        type_=sa.VARCHAR(length=200),
        existing_nullable=False,
    )

    op.alter_column(
        "suppliers",
        "supplier_code",
        existing_type=sa.String(length=30),
        type_=sa.VARCHAR(length=20),
        existing_nullable=False,
    )

    op.drop_column(
        "purchase_orders",
        "terms_conditions",
    )

    op.drop_column(
        "purchase_orders",
        "exchange_rate",
    )

    op.drop_column(
        "purchase_orders",
        "currency",
    )

    op.drop_column(
        "purchase_orders",
        "reference_number",
    )

    op.add_column(
        "purchase_invoices",
        sa.Column(
            "goods_receipt_id",
            sa.INTEGER(),
            nullable=False,
        ),
    )

    op.create_foreign_key(
        op.f("purchase_invoices_goods_receipt_id_fkey"),
        "purchase_invoices",
        "goods_receipts",
        ["goods_receipt_id"],
        ["id"],
    )

    op.create_index(
        op.f("ix_purchase_invoices_goods_receipt_id"),
        "purchase_invoices",
        ["goods_receipt_id"],
        unique=False,
    )