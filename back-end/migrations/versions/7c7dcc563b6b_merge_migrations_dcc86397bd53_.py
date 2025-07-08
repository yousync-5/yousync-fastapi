"""merge migrations: dcc86397bd53 + e1a9d06a0c6a

Revision ID: 7c7dcc563b6b
Revises: dcc86397bd53, e1a9d06a0c6a
Create Date: 2025-07-07 17:19:45.441503

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c7dcc563b6b'
down_revision: Union[str, Sequence[str], None] = ('dcc86397bd53', 'e1a9d06a0c6a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
