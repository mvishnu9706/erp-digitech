"""add customer service portal access

Revision ID: f5ad77c22fdb
Revises: b69784b573a6
Create Date: 2026-08-24
"""

from alembic import op
import sqlalchemy as sa


# ============================================================
# Revision identifiers
# ============================================================

revision = "f5ad77c22fdb"

down_revision = "b69784b573a6"

branch_labels = None

depends_on = None


# ============================================================
# Upgrade
# ============================================================

def upgrade() -> None:

    # --------------------------------------------------------
    # 1. Add service_enabled temporarily as nullable
    # --------------------------------------------------------

    op.add_column(
        "customers",
        sa.Column(
            "service_enabled",
            sa.Boolean(),
            nullable=True,
            server_default=sa.false(),
        ),
    )

    # --------------------------------------------------------
    # 2. Existing customers
    #
    # Existing customers should NOT automatically receive
    # service portal access.
    # --------------------------------------------------------

    op.execute(
        """
        UPDATE customers
        SET service_enabled = FALSE
        WHERE service_enabled IS NULL
        """
    )

    # --------------------------------------------------------
    # 3. Make the column NOT NULL
    # --------------------------------------------------------

    op.alter_column(
        "customers",
        "service_enabled",
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.false(),
    )


# ============================================================
# Downgrade
# ============================================================

def downgrade() -> None:

    op.drop_column(
        "customers",
        "service_enabled",
    )