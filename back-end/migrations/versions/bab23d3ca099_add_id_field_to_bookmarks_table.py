"""Add id field to bookmarks table

Revision ID: bab23d3ca099
Revises: 844f39fddc02
Create Date: 2025-07-12 18:08:28.486145

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bab23d3ca099'
down_revision: Union[str, Sequence[str], None] = '844f39fddc02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. 먼저 nullable한 id 컬럼 추가
    op.add_column('bookmarks', sa.Column('id', sa.Integer(), nullable=True))
    
    # 2. 기존 데이터에 id 값 할당 (ROW_NUMBER 사용)
    op.execute("""
        UPDATE bookmarks 
        SET id = subquery.row_num 
        FROM (
            SELECT user_id, token_id, 
                   ROW_NUMBER() OVER (ORDER BY created_at, user_id, token_id) as row_num
            FROM bookmarks
        ) AS subquery 
        WHERE bookmarks.user_id = subquery.user_id 
        AND bookmarks.token_id = subquery.token_id
    """)
    
    # 3. id 컬럼을 NOT NULL로 변경
    op.alter_column('bookmarks', 'id', nullable=False)
    
    # 4. id를 primary key로 설정
    op.create_primary_key('bookmarks_pkey', 'bookmarks', ['id'])
    
    # 5. id 컬럼에 인덱스 생성
    op.create_index(op.f('ix_bookmarks_id'), 'bookmarks', ['id'], unique=False)
    
    # 6. (user_id, token_id)에 unique constraint 추가
    op.create_unique_constraint('uq_user_token_bookmark', 'bookmarks', ['user_id', 'token_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # 역순으로 되돌리기
    op.drop_constraint('uq_user_token_bookmark', 'bookmarks', type_='unique')
    op.drop_index(op.f('ix_bookmarks_id'), table_name='bookmarks')
    op.drop_constraint('bookmarks_pkey', 'bookmarks', type_='primary')
    op.drop_column('bookmarks', 'id')
