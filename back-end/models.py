from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, JSON  # SQLAlchemy 데이터 타입들
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
    background_pitch_values = Column(JSON)  # 배경음 피치 값들을 JSON 배열로 저장
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # 생성 시간 (자동 설정)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())  # 수정 시간 (자동 업데이트)

# 영화 테이블 모델 - 영화 기본 정보를 저장
class Movie(Base):
    __tablename__ = "movies"  # 실제 데이터베이스 테이블 이름
    
    id = Column(Integer, primary_key=True, index=True)  # 기본키, 자동증가
    actor = Column(String, index=True)  # 주연배우 이름 (검색용 인덱스 생성)
    total_time = Column(Integer)  # 영화 총 재생시간 (분 단위)
    category = Column(String, index=True)  # 영화 카테고리 (로맨스, 액션 등, 검색용 인덱스)
    url = Column(String)  # 유튜브 영상 URL
    bookmark = Column(Boolean, default=False)  # 북마크 여부 (기본값: False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # 생성 시간 (자동 설정)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())  # 수정 시간 (자동 업데이트)
