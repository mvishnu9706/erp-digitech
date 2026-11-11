"""add rental bills

Revision ID: 7a468615aa60
Revises: d279ac6fa03f
Create Date: 2026-09-12 14:32:30.089382

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# =====================================================
# REVISION IDENTIFIERS
# =====================================================

revision: str = "7a468615aa60"

down_revision: Union[str, Sequence[str], None] = "d279ac6fa03f"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


# =====================================================
# UPGRADE
# =====================================================

def upgrade() -> None:
    """Upgrade schema."""

    # =================================================
    # REMOVE DELIVERY CHALLAN REFERENCE FROM
    # SALES INVOICES FIRST
    #
    # This MUST happen before dropping delivery_challans.
    # =================================================

    op.drop_index(
        op.f("ix_sales_invoices_delivery_challan_id"),
        table_name="sales_invoices"
    )

    op.drop_constraint(
        op.f("sales_invoices_delivery_challan_id_fkey"),
        "sales_invoices",
        type_="foreignkey"
    )

    op.drop_column(
        "sales_invoices",
        "delivery_challan_id"
    )

    # =================================================
    # REMOVE OLD DELIVERY CHALLAN TABLES
    #
    # Child table first, parent table second.
    # =================================================

    # -------------------------------------------------
    # Delivery Challan Items
    # -------------------------------------------------

    op.drop_index(
        op.f("ix_delivery_challan_items_delivery_challan_id"),
        table_name="delivery_challan_items"
    )

    op.drop_index(
        op.f("ix_delivery_challan_items_id"),
        table_name="delivery_challan_items"
    )

    op.drop_index(
        op.f("ix_delivery_challan_items_product_id"),
        table_name="delivery_challan_items"
    )

    op.drop_index(
        op.f("ix_delivery_challan_items_sales_order_item_id"),
        table_name="delivery_challan_items"
    )

    op.drop_table(
        "delivery_challan_items"
    )

    # -------------------------------------------------
    # Delivery Challans
    # -------------------------------------------------

    op.drop_index(
        op.f("ix_delivery_challans_customer_id"),
        table_name="delivery_challans"
    )

    op.drop_index(
        op.f("ix_delivery_challans_dc_number"),
        table_name="delivery_challans"
    )

    op.drop_index(
        op.f("ix_delivery_challans_id"),
        table_name="delivery_challans"
    )

    op.drop_index(
        op.f("ix_delivery_challans_sales_order_id"),
        table_name="delivery_challans"
    )

    op.drop_index(
        op.f("ix_delivery_challans_status"),
        table_name="delivery_challans"
    )

    op.drop_index(
        op.f("ix_delivery_challans_warehouse_id"),
        table_name="delivery_challans"
    )

    op.drop_table(
        "delivery_challans"
    )

    # =================================================
    # REMOVE OLD ACCOUNTING TABLES
    # =================================================

    # -------------------------------------------------
    # Journal Entry Lines
    #
    # Child table must be removed before journal_entries.
    # -------------------------------------------------

    op.drop_index(
        op.f("ix_journal_entry_lines_account_id"),
        table_name="journal_entry_lines"
    )

    op.drop_index(
        op.f("ix_journal_entry_lines_id"),
        table_name="journal_entry_lines"
    )

    op.drop_index(
        op.f("ix_journal_entry_lines_journal_entry_id"),
        table_name="journal_entry_lines"
    )

    op.drop_table(
        "journal_entry_lines"
    )

    # -------------------------------------------------
    # Journal Entries
    # -------------------------------------------------

    op.drop_index(
        op.f("ix_journal_entries_id"),
        table_name="journal_entries"
    )

    op.drop_index(
        op.f("ix_journal_entries_journal_number"),
        table_name="journal_entries"
    )

    op.drop_index(
        op.f("ix_journal_entries_voucher_type"),
        table_name="journal_entries"
    )

    op.drop_table(
        "journal_entries"
    )

    # -------------------------------------------------
    # Chart Of Accounts
    # -------------------------------------------------

    op.drop_index(
        op.f("ix_chart_of_accounts_account_code"),
        table_name="chart_of_accounts"
    )

    op.drop_index(
        op.f("ix_chart_of_accounts_account_type"),
        table_name="chart_of_accounts"
    )

    op.drop_index(
        op.f("ix_chart_of_accounts_id"),
        table_name="chart_of_accounts"
    )

    op.drop_table(
        "chart_of_accounts"
    )

    # =================================================
    # RENTAL BILLS
    # =================================================

    # -------------------------------------------------
    # Add new columns temporarily as nullable
    # -------------------------------------------------

    op.add_column(
        "rental_bills",
        sa.Column(
            "copies_used",
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        "rental_bills",
        sa.Column(
            "paid_amount",
            sa.Numeric(
                precision=12,
                scale=2
            ),
            nullable=True
        )
    )

    op.add_column(
        "rental_bills",
        sa.Column(
            "outstanding_amount",
            sa.Numeric(
                precision=12,
                scale=2
            ),
            nullable=True
        )
    )

    # -------------------------------------------------
    # Populate new columns for existing records
    # -------------------------------------------------

    op.execute(
        """
        UPDATE rental_bills
        SET
            copies_used = COALESCE(
                billable_copies,
                total_copies,
                0
            ),
            paid_amount = 0,
            outstanding_amount = COALESCE(
                total_amount,
                0
            )
        """
    )

    # -------------------------------------------------
    # Make new columns NOT NULL
    # -------------------------------------------------

    op.alter_column(
        "rental_bills",
        "copies_used",
        existing_type=sa.Integer(),
        nullable=False
    )

    op.alter_column(
        "rental_bills",
        "paid_amount",
        existing_type=sa.Numeric(
            precision=12,
            scale=2
        ),
        nullable=False
    )

    op.alter_column(
        "rental_bills",
        "outstanding_amount",
        existing_type=sa.Numeric(
            precision=12,
            scale=2
        ),
        nullable=False
    )

    # =================================================
    # RENTAL BILL COLUMN CHANGES
    # =================================================

    op.alter_column(
        "rental_bills",
        "bill_number",
        existing_type=sa.VARCHAR(length=30),
        type_=sa.String(length=50),
        existing_nullable=False
    )

    op.alter_column(
        "rental_bills",
        "billing_month",
        existing_type=sa.VARCHAR(length=20),
        type_=sa.String(length=7),
        existing_nullable=False
    )

    op.alter_column(
        "rental_bills",
        "previous_meter",
        existing_type=sa.INTEGER(),
        nullable=False
    )

    op.alter_column(
        "rental_bills",
        "current_meter",
        existing_type=sa.INTEGER(),
        nullable=False
    )

    op.alter_column(
        "rental_bills",
        "cost_per_copy",
        existing_type=sa.NUMERIC(
            precision=12,
            scale=4
        ),
        type_=sa.Numeric(
            precision=12,
            scale=2
        ),
        nullable=False
    )

    op.alter_column(
        "rental_bills",
        "total_amount",
        existing_type=sa.NUMERIC(
            precision=12,
            scale=2
        ),
        nullable=False
    )

    op.alter_column(
        "rental_bills",
        "payment_status",
        existing_type=sa.VARCHAR(length=20),
        nullable=False
    )

    op.alter_column(
        "rental_bills",
        "created_by",
        existing_type=sa.INTEGER(),
        nullable=False
    )

    op.alter_column(
        "rental_bills",
        "created_at",
        existing_type=postgresql.TIMESTAMP(
            timezone=True
        ),
        nullable=False,
        existing_server_default=sa.text("now()")
    )

    op.alter_column(
        "rental_bills",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(
            timezone=True
        ),
        nullable=False,
        existing_server_default=sa.text("now()")
    )

    # =================================================
    # RENTAL BILL INDEXES
    # =================================================

    op.create_index(
        op.f("ix_rental_bills_billing_month"),
        "rental_bills",
        ["billing_month"],
        unique=False
    )

    op.create_index(
        op.f("ix_rental_bills_customer_id"),
        "rental_bills",
        ["customer_id"],
        unique=False
    )

    op.create_index(
        op.f("ix_rental_bills_machine_id"),
        "rental_bills",
        ["machine_id"],
        unique=False
    )

    op.create_index(
        op.f("ix_rental_bills_payment_status"),
        "rental_bills",
        ["payment_status"],
        unique=False
    )

    # =================================================
    # ONE BILL PER MACHINE PER MONTH
    # =================================================

    op.create_unique_constraint(
        "uq_rental_bill_machine_month",
        "rental_bills",
        [
            "machine_id",
            "billing_month"
        ]
    )

    # =================================================
    # RENTAL BILL FOREIGN KEYS
    # =================================================

    # -------------------------------------------------
    # Remove old foreign keys
    # -------------------------------------------------

    op.drop_constraint(
        op.f("rental_bills_amc_contract_id_fkey"),
        "rental_bills",
        type_="foreignkey"
    )

    op.drop_constraint(
        op.f("rental_bills_created_by_fkey"),
        "rental_bills",
        type_="foreignkey"
    )

    op.drop_constraint(
        op.f("rental_bills_machine_id_fkey"),
        "rental_bills",
        type_="foreignkey"
    )

    op.drop_constraint(
        op.f("rental_bills_customer_id_fkey"),
        "rental_bills",
        type_="foreignkey"
    )

    op.drop_constraint(
        op.f("rental_bills_updated_by_fkey"),
        "rental_bills",
        type_="foreignkey"
    )

    # -------------------------------------------------
    # Create new foreign keys
    # -------------------------------------------------

    op.create_foreign_key(
        "rental_bills_machine_id_fkey",
        "rental_bills",
        "machines",
        ["machine_id"],
        ["id"],
        ondelete="RESTRICT"
    )

    op.create_foreign_key(
        "rental_bills_created_by_fkey",
        "rental_bills",
        "users",
        ["created_by"],
        ["id"],
        ondelete="RESTRICT"
    )

    op.create_foreign_key(
        "rental_bills_customer_id_fkey",
        "rental_bills",
        "customers",
        ["customer_id"],
        ["id"],
        ondelete="RESTRICT"
    )

    op.create_foreign_key(
        "rental_bills_updated_by_fkey",
        "rental_bills",
        "users",
        ["updated_by"],
        ["id"],
        ondelete="RESTRICT"
    )

    # =================================================
    # REMOVE OLD RENTAL BILL COLUMNS
    # =================================================

    op.drop_column(
        "rental_bills",
        "free_copies"
    )

    op.drop_column(
        "rental_bills",
        "gst_percentage"
    )

    op.drop_column(
        "rental_bills",
        "billable_copies"
    )

    op.drop_column(
        "rental_bills",
        "total_copies"
    )

    op.drop_column(
        "rental_bills",
        "gst_amount"
    )

    op.drop_column(
        "rental_bills",
        "subtotal"
    )

    op.drop_column(
        "rental_bills",
        "amc_contract_id"
    )


# =====================================================
# DOWNGRADE
# =====================================================

def downgrade() -> None:
    """
    Downgrade is intentionally unsupported.

    Delivery Challan and old accounting modules were
    intentionally removed from the application.
    """

    raise NotImplementedError(
        "Downgrade is not supported for this migration because "
        "Delivery Challan, Chart of Accounts and Journal Entry "
        "modules were intentionally removed."
    )