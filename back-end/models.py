from sqlalchemy import Column, Integer, String, Float, Text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    director = Column(String)
    release_year = Column(Integer)
    category = Column(String, index=True)
    youtube_url = Column(String, unique=True, nullable=False)
    total_time = Column(Integer)
    bookmark = Column(Boolean, default=False)
    
    # 관계
    scripts = relationship("Script", back_populates="movie", cascade="all, delete")

class Actor(Base):
    __tablename__ = "actors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    tmdb_id = Column(Integer, unique=True, nullable=True)
    
    # 관계
    scripts = relationship("Script", back_populates="actor")

class Script(Base):
    __tablename__ = "scripts"
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    actor_id = Column(Integer, ForeignKey("actors.id"), nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    script = Column(Text, nullable=False)
    translation = Column(Text)
    url = Column(String)
    actor_pitch_values = Column(JSON)
    background_audio_url = Column(String)
    
    # 관계
    movie = relationship("Movie", back_populates="scripts")
    actor = relationship("Actor", back_populates="scripts")

class MovieActor(Base):
    __tablename__ = "movie_actors"
    
    movie_id = Column(Integer, ForeignKey("movies.id"), primary_key=True)
    actor_id = Column(Integer, ForeignKey("actors.id"), primary_key=True)
    character_name = Column(String)  # 극중 역할명

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
