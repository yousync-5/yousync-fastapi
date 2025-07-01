from sqlalchemy import Column, Integer, String, Float, Text, JSON, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Token(Base):
    __tablename__ = "tokens"  # 토큰 단위 (token_id)

    id = Column(Integer, primary_key=True, index=True)  # token_id
    
    token_name = Column(String, nullable=False)
    actor_name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)

    s3_textgrid_url = Column(Text, nullable=True)
    s3_pitch_url = Column(Text, nullable=True)
    s3_bgvoice_url = Column(Text, nullable=True)
    youtube_url  = Column(Text, nullable=True)
    # 관계
    scripts = relationship("Script", back_populates="token", cascade="all, delete")

class Actor(Base):
    __tablename__ = "actors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    
    # 관계
    # scripts = relationship("Script", back_populates="actor")

class Script(Base):
    __tablename__ = "scripts"  # 문장 단위

    id = Column(Integer, primary_key=True, index=True)  # 문장 고유 ID
    token_id = Column(Integer, ForeignKey("tokens.id"), nullable=False) # token_id와 연결
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    script = Column(Text, nullable=False)
    translation = Column(Text, nullable=True)

    token = relationship("Token", back_populates="scripts")

# class MovieActor(Base):
#     __tablename__ = "movie_actors"
    
#     movie_id = Column(Integer, ForeignKey("movies.id"), primary_key=True)
#     actor_id = Column(Integer, ForeignKey("actors.id"), primary_key=True)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    token_id = Column(Integer, ForeignKey("tokens.id"), nullable=False)
    status = Column(String, nullable=False)
    progress = Column(Integer, nullable=False)
    result = Column(JSON, nullable=True)  # analysis_results 점수만 저장
    message = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    token = relationship("Token")

# Token 에 역참조(optional)
Token.analysis_results = relationship(
    "AnalysisResult", back_populates="token", cascade="all, delete"
)