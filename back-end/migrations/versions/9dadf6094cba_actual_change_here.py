"""actual change here

Revision ID: 9dadf6094cba
Revises: ab48135d33f1
Create Date: 2025-07-10 14:34:05.742324

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9dadf6094cba'
down_revision: Union[str, Sequence[str], None] = 'ab48135d33f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 확장 설치만 남겨 두세요
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

def downgrade():
    op.execute("DROP EXTENSION IF EXISTS pg_trgm;")
