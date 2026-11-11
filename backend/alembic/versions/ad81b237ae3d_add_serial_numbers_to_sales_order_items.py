"""add serial numbers to sales order items

Revision ID: ad81b237ae3d
Revises: ff2f5bee2143
Create Date: 2026-08-14 12:39:17.228269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad81b237ae3d'
down_revision: Union[str, Sequence[str], None] = 'ff2f5bee2143'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
