# revision identifiers, used by Alembic.
revision = '0000_root'    # 원하는 ID로 지정
down_revision = None      # ← 여기가 핵심: None으로 설정해 더 이상 내려가지 않음
branch_labels = None
depends_on = None

def upgrade():
    # 이미 스키마가 최신이라면 빈 함수로 둡니다.
    pass

def downgrade():
    pass
