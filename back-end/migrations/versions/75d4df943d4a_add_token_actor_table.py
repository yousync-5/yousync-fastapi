from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

revision = "75d4df943d4a"
down_revision = "79e6d9b271d9"
branch_labels = None
depends_on = None

def upgrade():
    # ① token_actors 테이블
    op.create_table(
        "token_actors",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("token_id", sa.Integer, sa.ForeignKey("tokens.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", sa.Integer, sa.ForeignKey("actors.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("token_id", "actor_id", name="uq_token_actor"),
    )

    # ② 인덱스(조회 가속용)
    op.create_index("ix_token_actors_token_id", "token_actors", ["token_id"])
    op.create_index("ix_token_actors_actor_id", "token_actors", ["actor_id"])

    # ③ 기존 데이터 이관 (PostgreSQL 기준)
    bind = op.get_bind()
    bind.execute(text("""
        INSERT INTO token_actors (token_id, actor_id)
        SELECT t.id, a.id
        FROM tokens t
        JOIN actors a ON a.name = t.actor_name
        ON CONFLICT DO NOTHING
    """))

def downgrade():
    op.drop_index("ix_token_actors_actor_id", table_name="token_actors")
    op.drop_index("ix_token_actors_token_id", table_name="token_actors")
    op.drop_table("token_actors")
