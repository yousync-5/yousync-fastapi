from database import SessionLocal, engine
from models import Base, Script, Movie

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)


# 더미 데이터 추가
def add_dummy_data():
    db = SessionLocal()
    try:
        # Script 더미 데이터
        script_data = Script(
            actor="emma watson",
            start_time=2.1,
            end_time=2.6,
            script="Now we just look down and worry about our place.",
            translation="이제 우린 그냥 고개 숙이고, 우리 자리나 걱정하면서 사는 거야.",
            url="https://youtube.com",
            actor_pitch_values=[200, 240, 220, 234, 232, 221, 210, 205, 253],
            background_pitch_values=[
                300, 231, 452, 540, 480, 650, 439, 530, 450
            ]
        )
        
        # Movie 더미 데이터
        movie_data = Movie(
            actor="Natalie Portman",
            total_time=34,
            category="로맨스",
            url="https://youtube.com",
            bookmark=True
        )
        
        db.add(script_data)
        db.add(movie_data)
        db.commit()
        
        print("✅ 더미 데이터가 성공적으로 추가되었습니다!")
        print(f"📝 Script ID: {script_data.id}")
        print(f"🎬 Movie ID: {movie_data.id}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    add_dummy_data()
