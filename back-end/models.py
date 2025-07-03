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
    youtube_url = Column(
        Text,
        ForeignKey("urls.youtube_url", ondelete="CASCADE"),  # 핵심!
        nullable=False,
        index=True,
    )
    # 관계
    url = relationship("URL", back_populates="tokens")
    scripts = relationship("Script",
                        back_populates="token",
                        cascade="all, delete",
                        passive_deletes=True)          # ✅   
    analysis_results = relationship("AnalysisResult", back_populates="token", cascade="all, delete")
    

class URL(Base):
    __tablename__ = "urls"
    youtube_url = Column(Text, primary_key=True)   
    actor_id    = Column(Integer,
                         ForeignKey("actors.id", ondelete="CASCADE"),
                         nullable=False, index=True)


    actor  = relationship("Actor", back_populates="urls")
    tokens = relationship("Token",
                          back_populates="url",
                          cascade="all, delete",
                          passive_deletes=True)



class Actor(Base):
    __tablename__ = "actors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    
    # 관계
    urls = relationship("URL",
                        back_populates="actor",
                        cascade="all, delete",
                        passive_deletes=True)



class Script(Base):
    __tablename__ = "scripts"  # 문장 단위

    id = Column(Integer, primary_key=True, index=True)  # 문장 고유 ID
    token_id = Column(
        Integer,
        ForeignKey("tokens.id", ondelete="CASCADE"),   # ✅ DB-레벨 연쇄 삭제
        nullable=False,
        index=True,
    )    
    
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    script = Column(Text, nullable=False)
    translation = Column(Text, nullable=True)

    token = relationship(
        "Token",
        back_populates="scripts",
        passive_deletes=True,                         # ✅ DB에 맡긴다
    )    
    words = relationship(
        "ScriptWord",
        back_populates="script",
        cascade="all, delete",
        passive_deletes=True,            # ➕
    )


class ScriptWord(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    script_id = Column(
        Integer,
        ForeignKey("scripts.id", ondelete="CASCADE"),  # ← 핵심
        nullable=False,
        index=True,
    )
    word = Column(String)
    start_time = Column(Float)
    end_time = Column(Float)
    probability = Column(Float)

    # 관계 설정
    script = relationship(
        "Script",
        back_populates="words",
        passive_deletes=True,           # DB가 직접 삭제하도록
    )



class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # 소셜 로그인 시에는 null
    
    # 소셜 로그인 관련 필드
    google_id = Column(String, unique=True, index=True, nullable=True)
    profile_picture = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    login_type = Column(String, default="email")  # "email" or "google"
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())



class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    token_id = Column(Integer,
                  ForeignKey("tokens.id", ondelete="CASCADE"),
                  nullable=False)
    status = Column(String, nullable=False)
    progress = Column(Integer, nullable=False)
    result = Column(JSON, nullable=True)  # analysis_results 점수만 저장
    message = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    token = relationship("Token", back_populates="analysis_results") #??
