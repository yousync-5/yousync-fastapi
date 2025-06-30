from models import Base
from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("🔴 외래키 의존성 제거를 위해 테이블 강제 삭제 중...")
    # conn.execute(text("DROP TABLE IF EXISTS movie_actors"))
    conn.execute(text("DROP TABLE IF EXISTS scripts"))
    conn.execute(text("DROP TABLE IF EXISTS tokens"))
    conn.execute(text("DROP TABLE IF EXISTS actors"))
    conn.commit()

print("🟢 새 테이블 생성 중...")
Base.metadata.create_all(bind=engine)
print("✅ DB 초기화 완료")
