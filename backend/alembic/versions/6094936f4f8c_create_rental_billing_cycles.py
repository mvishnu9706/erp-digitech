"""create rental billing cycles

Revision ID: 6094936f4f8c
Revises: 7a468615aa60
Create Date: 2026-09-18 10:37:26.987666

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6094936f4f8c"
down_revision: Union[str, Sequence[str], None] = "7a468615aa60"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create rental billing cycles table."""

    op.create_table(
        "rental_billing_cycles",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "active_billing_month",
            sa.String(length=7),
            nullable=False,
        ),

        sa.Column(
            "cycle_started_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_rental_billing_cycles_id"),
        "rental_billing_cycles",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_rental_billing_cycles_active_billing_month"),
        "rental_billing_cycles",
        ["active_billing_month"],
        unique=False,
    )


def downgrade() -> None:
    """Drop rental billing cycles table."""

    op.drop_index(
        op.f("ix_rental_billing_cycles_active_billing_month"),
        table_name="rental_billing_cycles",
    )

    op.drop_index(
        op.f("ix_rental_billing_cycles_id"),
        table_name="rental_billing_cycles",
    )

    op.drop_table("rental_billing_cycles")