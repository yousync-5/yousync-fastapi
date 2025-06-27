from sqlalchemy import text
from sqlalchemy.orm import Session
from database import engine
from models import Base

# 1. 커넥션 열고 수동 DROP CASCADE 수행
with engine.connect() as conn:
    print("🔴 외래키 의존성 제거를 위해 테이블 강제 삭제 중...")
    conn.execute(text("DROP TABLE IF EXISTS movie_actors CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS scripts CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS movies CASCADE"))
    conn.commit()

# 2. 전체 재생성
print("🟢 새 테이블 생성 중...")
Base.metadata.create_all(bind=engine)
print("✅ DB 초기화 완료")