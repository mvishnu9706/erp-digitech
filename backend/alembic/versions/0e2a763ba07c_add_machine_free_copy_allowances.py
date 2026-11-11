"""add machine free copy allowances

Revision ID: 0e2a763ba07c
Revises: 31ca6e163792
Create Date: 2026-10-23 10:31:50.075391

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0e2a763ba07c"
down_revision: Union[str, Sequence[str], None] = "31ca6e163792"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add per-format monthly free-copy allowances to machines."""
    op.add_column(
        "machines",
        sa.Column(
            "a4_bw_free_copies",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )
    op.add_column(
        "machines",
        sa.Column(
            "a4_color_free_copies",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )
    op.add_column(
        "machines",
        sa.Column(
            "a3_bw_free_copies",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )
    op.add_column(
        "machines",
        sa.Column(
            "a3_color_free_copies",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Remove the per-format monthly free-copy allowances."""
    op.drop_column("machines", "a3_color_free_copies")
    op.drop_column("machines", "a3_bw_free_copies")
    op.drop_column("machines", "a4_color_free_copies")
    op.drop_column("machines", "a4_bw_free_copies")
