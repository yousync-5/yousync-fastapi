"""initial migration

Revision ID: f2f36497c06a
Revises: 
Create Date: 2025-07-17 20:37:21.105156

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2f36497c06a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'youtube_process_jobs', 'tokens', ['token_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'youtube_process_jobs', 'users', ['user_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'youtube_process_jobs', type_='foreignkey')
    op.drop_constraint(None, 'youtube_process_jobs', type_='foreignkey')
    # ### end Alembic commands ###
