"""drop FK from youtube_process_jobs

Revision ID: 7777f85d9e86
Revises: bab23d3ca099
Create Date: 2025-07-15 19:05:20.612520

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7777f85d9e86'
down_revision: Union[str, Sequence[str], None] = 'bab23d3ca099'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # user_id 외래키 제약 제거
    op.drop_constraint(
        'youtube_process_jobs_user_id_fkey',
        'youtube_process_jobs',
        type_='foreignkey'
    )
    # token_id 외래키 제약 제거
    op.drop_constraint(
        'youtube_process_jobs_token_id_fkey',
        'youtube_process_jobs',
        type_='foreignkey'
    )
def downgrade():
    op.create_foreign_key(
        'youtube_process_jobs_user_id_fkey',
        'youtube_process_jobs',
        'users',
        ['user_id'],
        ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'youtube_process_jobs_token_id_fkey',
        'youtube_process_jobs',
        'tokens',
        ['token_id'],
        ['id'],
        ondelete='SET NULL'
    )

