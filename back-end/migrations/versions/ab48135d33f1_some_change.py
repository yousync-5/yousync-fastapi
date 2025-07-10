"""some change

Revision ID: ab48135d33f1
Revises: b70f90113738
Create Date: 2025-07-10 14:28:19.117959

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab48135d33f1'
down_revision: Union[str, Sequence[str], None] = 'b70f90113738'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
