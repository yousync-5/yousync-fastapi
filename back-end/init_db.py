# init_db.py
from models import Base  # 모델 정의
from database import engine    # SQLAlchemy 엔진

print("🔴 기존 테이블 삭제 중...")
Base.metadata.drop_all(bind=engine)

print("🟢 새 테이블 생성 중...")
Base.metadata.create_all(bind=engine)

print("✅ DB 초기화 완료")