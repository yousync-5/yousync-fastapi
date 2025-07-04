"""Add index on view_count

Revision ID: e1a9d06a0c6a
Revises: b5ef67876f8e
Create Date: 2025-07-04 14:27:49.114595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision = 'e1a9d06a0c6a'
down_revision = "b5ef67876f8e"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f('ix_tokens_view_count'), 'tokens', ['view_count'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_tokens_view_count'), table_name='tokens')
