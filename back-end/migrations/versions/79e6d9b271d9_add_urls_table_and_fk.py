from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers
revision = "79e6d9b271d9"
down_revision = "8f5d6297aa14"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) urls 테이블 먼저
    op.create_table(
        "urls",
        sa.Column("youtube_url", sa.Text, primary_key=True),
        sa.Column("actor_id", sa.Integer,
                  sa.ForeignKey("actors.id", ondelete="CASCADE"),
                  nullable=False, index=True),
    )

    bind = op.get_bind()

    # 2) 기존 토큰들의 youtube_url → urls 테이블에 채워넣기
    bind.execute(text("""
        INSERT INTO urls (youtube_url, actor_id)
        SELECT DISTINCT t.youtube_url,
               a.id
        FROM tokens t
        JOIN actors a ON a.name = t.actor_name      -- 매핑
        WHERE t.youtube_url IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM urls u
              WHERE u.youtube_url = t.youtube_url
          )
    """))

    # 3) 이제 FK 제약을 건다
    op.create_foreign_key(
        "fk_tokens_youtube_url",
        source_table="tokens",
        referent_table="urls",
        local_cols=["youtube_url"],
        remote_cols=["youtube_url"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_tokens_youtube_url", "tokens", type_="foreignkey")
    op.drop_table("urls")
