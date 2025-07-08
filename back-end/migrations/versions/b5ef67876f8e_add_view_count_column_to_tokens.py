"""Add view_count column to tokens

Revision ID: b5ef67876f8e
Revises: 610f93aeb2e8
Create Date: 2025-07-04 13:37:56.827381

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision = 'b5ef67876f8e'
down_revision = "610f93aeb2e8"
branch_labels = None
depends_on = None

def upgrade():
    pass
    # op.add_column(
    #     'tokens',
    #     sa.Column('view_count',
    #               sa.Integer(),
    #               nullable=False,
    #               server_default='0')
    # )
    # 기존 데이터가 null 문제가 없도록 server_default='0' 설정

def downgrade():
    op.drop_column('tokens', 'view_count')