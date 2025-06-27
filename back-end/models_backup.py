from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, JSON  ,ForeignKey # ForeignKey 추가# SQLAlchemy 데이터 타입들
from sqlalchemy.orm import relationship # relationship 추가
from sqlalchemy.sql import func  # 데이터베이스 함수들 (현재 시간 등)
from database import Base  # 데이터베이스 베이스 클래스

# 스크립트 테이블 모델 - 영화/드라마 대사 정보를 저장
class Script(Base):
    __tablename__ = "scripts"  # 실제 데이터베이스 테이블 이름
    
    id = Column(Integer, primary_key=True, index=True)  # 기본키, 자동증가
    actor = Column(String, index=True)  # 배우 이름 (검색용 인덱스 생성)
    start_time = Column(Float)  # 대사 시작 시간 (초 단위, 소수점 허용)
    end_time = Column(Float)  # 대사 끝 시간 (초 단위, 소수점 허용)
    script = Column(Text)  # 대사 원문 (긴 텍스트 저장 가능)
    translation = Column(Text)  # 대사 번역문 (긴 텍스트 저장 가능)
    url = Column(String)  # 유튜브 영상 URL
    actor_pitch_values = Column(JSON)  # 배우 음성 피치 값들을 JSON 배열로 저장
    background_audio_url= Column(String, nullable=True)  # 배경음을 aws s3서버에서 string으로 받아옴

    # === [추가] 외래 키 및 관계 설정 ===
    movie_id = Column(Integer, ForeignKey("movies.id"))  # movies 테이블의 id를 참조하는 외래 키
    movie = relationship("Movie", back_populates="scripts") # Movie 모델과의 관계 설정 (역참조)


# 영화 테이블 모델 - 영화 기본 정보를 저장
class Movie(Base):
    __tablename__ = "movies"  # 실제 데이터베이스 테이블 이름
    
    id = Column(Integer, primary_key=True, index=True)  # 기본키, 자동증가
    actor = Column(String, index=True)  # 주연배우 이름 (검색용 인덱스 생성)
    total_time = Column(Integer)  # 영화 총 재생시간 (분 단위)
    category = Column(String, index=True)  # 영화 카테고리 (로맨스, 액션 등, 검색용 인덱스)
    url = Column(String)  # 유튜브 영상 URL
    bookmark = Column(Boolean, default=False)  # 북마크 여부 (기본값: False)

    # === [추가] 관계 설정 ===
    # 하나의 Movie가 여러 Script를 가질 수 있음 (일대다)
    # cascade="all, delete": Movie가 삭제되면 관련된 모든 Script도 함께 삭제됨
    scripts = relationship("Script", back_populates="movie", cascade="all, delete")


class User(Base):
    __tablename__ = "users"  # 실제 데이터베이스 테이블 이름
    
    id = Column(Integer, primary_key=True, index=True)  # 기본키, 자동증가
    username = Column(String, unique=True, index=True)  # 사용자 이름 (고유값, 검색용 인덱스)
    email = Column(String, unique=True, index=True)  # 이메일 (고유값, 검색용 인덱스)
    hashed_password = Column(String)  # 해시된 비밀번호

    #is_superuser = Column(Boolean, default=False)  # 관리자 여부 (기본값: False)

class Actor(Base):
    __tablename__ = "actors"  # 실제 데이터베이스 테이블 이름
    
    id = Column(Integer, primary_key=True, index=True)  # 기본키, 자동증가
    name = Column(String, unique=True, index=True)  # 배우 이름 (고유값, 검색용 인덱스)
    tmdb   # The Movie DB의 고유 ID
    profile_image = Column(String, nullable=True)  # 프로필 이미지 URL (nullable=True: 값이 없을 수도 있음)
    
    # 영화와의 관계 설정 (배우가 출연한 영화 목록)
    movies = relationship("Movie", secondary="movie_actors", back_populates="actors")

