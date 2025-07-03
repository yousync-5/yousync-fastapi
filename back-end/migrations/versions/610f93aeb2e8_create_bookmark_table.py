"""create bookmark table

Revision ID: 610f93aeb2e8
Revises: 99ed4b628e7d
Create Date: 2025-07-03 21:58:49.931831

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
# revision: str = '610f93aeb2e8'
# down_revision: Union[str, Sequence[str], None] = '99ed4b628e7d'
# branch_labels: Union[str, Sequence[str], None] = None
# depends_on: Union[str, Sequence[str], None] = None

revision = '610f93aeb2e8'
down_revision = "89c35b47055a"
branch_labels = None
depends_on = None



def upgrade():
    op.create_table(
        "bookmarks",
        sa.Column("user_id",  sa.Integer(), sa.ForeignKey("users.id",  ondelete="CASCADE"), primary_key=True),
        sa.Column("token_id", sa.Integer(), sa.ForeignKey("tokens.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_bookmarks_user_id",  "bookmarks", ["user_id"])
    op.create_index("ix_bookmarks_token_id", "bookmarks", ["token_id"])

def downgrade():
    op.drop_table("bookmarks")