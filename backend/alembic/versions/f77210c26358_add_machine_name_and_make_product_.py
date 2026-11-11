"""add machine name and make product nullable

Revision ID: f77210c26358
Revises: b0359f1b4573
Create Date: 2026-09-08 11:36:22.803280

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f77210c26358"
down_revision: Union[str, Sequence[str], None] = "b0359f1b4573"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add machine_name to the machines table.
    op.add_column(
        "machines",
        sa.Column(
            "machine_name",
            sa.String(length=200),
            nullable=True,
        ),
    )

    # Allow machines created from the Customer form
    # to exist without selecting a Product.
    op.alter_column(
        "machines",
        "product_id",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Before restoring product_id to NOT NULL, make sure
    # there are no machines without a product.
    connection = op.get_bind()

    null_product_count = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM machines
            WHERE product_id IS NULL
            """
        )
    ).scalar()

    if null_product_count and null_product_count > 0:
        raise RuntimeError(
            "Cannot downgrade migration f77210c26358 because "
            f"{null_product_count} machine(s) have product_id = NULL. "
            "Assign a product to these machines before downgrading."
        )

    # Restore product_id as NOT NULL.
    op.alter_column(
        "machines",
        "product_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    # Remove machine_name.
    op.drop_column(
        "machines",
        "machine_name" ,
    )