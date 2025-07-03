"""add actor_aliases table

Revision ID: 3a94977e87b6
Revises: 75d4df943d4a
Create Date: 2025-07-03 15:33:46.668271

"""
from alembic import op
import sqlalchemy as sa

revision = "3a94977e87b6"
down_revision = "75d4df943d4a"   # ← 현재 HEAD ID로 맞춰 주세요
branch_labels = None
depends_on = None

def upgrade():
    # 1) 테이블
    op.create_table(
        "actor_aliases",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("actor_id", sa.Integer,
                  sa.ForeignKey("actors.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.UniqueConstraint("actor_id", "name", name="uq_actor_alias"),
    )
    # 2) 인덱스
    op.create_index("ix_alias_name",  "actor_aliases", ["name"])

    # 3) (선택) pg_trgm + GIN 인덱스 ― 오타 검색용
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    op.execute("""
        CREATE INDEX ix_alias_name_trgm
        ON actor_aliases
        USING gin (name gin_trgm_ops);
    """)

def downgrade():
    op.drop_index("ix_alias_name_trgm", table_name="actor_aliases")
    op.drop_index("ix_alias_name",      table_name="actor_aliases")
    op.drop_table("actor_aliases")