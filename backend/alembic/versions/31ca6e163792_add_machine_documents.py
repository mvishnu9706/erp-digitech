"""add machine documents

Revision ID: 31ca6e163792
Revises: 38000051f6bc
Create Date: 2026-09-30 11:25:37.556764

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "31ca6e163792"
down_revision: Union[str, Sequence[str], None] = "38000051f6bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create machine documents table."""

    op.create_table(
        "machine_documents",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "machine_id",
            sa.Integer(),
            nullable=False
        ),

        # Rental Agreement PDF
        sa.Column(
            "rental_agreement",
            sa.LargeBinary(),
            nullable=True
        ),

        sa.Column(
            "rental_agreement_name",
            sa.String(length=255),
            nullable=True
        ),

        sa.Column(
            "rental_agreement_type",
            sa.String(length=100),
            nullable=True
        ),

        sa.Column(
            "rental_agreement_size",
            sa.Integer(),
            nullable=True
        ),

        # Installation Report PDF
        sa.Column(
            "installation_report",
            sa.LargeBinary(),
            nullable=True
        ),

        sa.Column(
            "installation_report_name",
            sa.String(length=255),
            nullable=True
        ),

        sa.Column(
            "installation_report_type",
            sa.String(length=100),
            nullable=True
        ),

        sa.Column(
            "installation_report_size",
            sa.Integer(),
            nullable=True
        ),

        # Audit
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False
        ),

        # Relationship with machines
        sa.ForeignKeyConstraint(
            ["machine_id"],
            ["machines.id"],
            ondelete="CASCADE"
        ),

        sa.PrimaryKeyConstraint("id")
    )

    # Primary key index
    op.create_index(
        op.f("ix_machine_documents_id"),
        "machine_documents",
        ["id"],
        unique=False
    )

    # One document record per machine
    op.create_index(
        op.f("ix_machine_documents_machine_id"),
        "machine_documents",
        ["machine_id"],
        unique=True
    )


def downgrade() -> None:
    """Remove machine documents table."""

    op.drop_index(
        op.f("ix_machine_documents_machine_id"),
        table_name="machine_documents"
    )

    op.drop_index(
        op.f("ix_machine_documents_id"),
        table_name="machine_documents"
    )

    op.drop_table("machine_documents")