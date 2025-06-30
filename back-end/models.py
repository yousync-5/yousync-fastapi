from sqlalchemy import Column, Integer, String, Float, Text, JSON, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    category = Column(String, index=True)
    youtube_url = Column(String, unique=True, nullable=False)
    total_time = Column(Integer)
    bookmark = Column(Boolean, default=False)
    full_background_audio_url = Column(String, nullable=True)  # 전체 배경음 (더빙 합성용)
    
    # 관계
    scripts = relationship("Script", back_populates="movie", cascade="all, delete")

class Actor(Base):
    __tablename__ = "actors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    
    # 관계
    scripts = relationship("Script", back_populates="actor")

class Script(Base):
    __tablename__ = "scripts"
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    actor_id = Column(Integer, ForeignKey("actors.id"), nullable=False) # actor 과의 종속성으로 없어도 될 필드 같음
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    script = Column(Text, nullable=False)
    translation = Column(Text, nullable=False)
    # url = Column(String)
    actor_pitch_values = Column(JSON, nullable=True)
    background_audio_url = Column(String, nullable=True)   # 구간별 배경음 (분석용)
    # user_voice_url = Column(String, nullable=True)         # 사용자 더빙 음성
    # user_voice_uploaded_at = Column(DateTime, default=func.now(), nullable=True)  # 더빙 업로드 시간
    
    # 관계
    movie = relationship("Movie", back_populates="scripts")
    actor = relationship("Actor", back_populates="scripts")

class MovieActor(Base):
    __tablename__ = "movie_actors"
    
    movie_id = Column(Integer, ForeignKey("movies.id"), primary_key=True)
    actor_id = Column(Integer, ForeignKey("actors.id"), primary_key=True)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
