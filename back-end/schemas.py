from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# === Actor Schemas ===
class ActorBase(BaseModel):
    name: str

class ActorCreate(ActorBase):
    pass

class Actor(ActorBase):
    id: int
    
    class Config:
        from_attributes = True

# === Script Schemas ===
class ScriptBase(BaseModel):
    movie_id: int
    actor_id: int
    start_time: float
    end_time: float
    script: str
    translation: Optional[str] = None
    url: Optional[str] = None
    actor_pitch_values: Optional[List[int]] = None
    background_audio_url: Optional[str] = None
    # user_voice_url: Optional[str] = None
    # user_voice_uploaded_at: Optional[datetime] = None

class ScriptCreate(ScriptBase):
    pass

class Script(ScriptBase):
    id: int
    actor: Optional[Actor] = None  # 배우 정보 포함
    
    class Config:
        from_attributes = True

# === Movie Schemas ===
class MovieBase(BaseModel):
    title: str
    category: Optional[str] = None
    youtube_url: str
    total_time: Optional[int] = None
    bookmark: bool = False
    full_background_audio_url: Optional[str] = None

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int
    scripts: List[Script] = []  # 영화에 속한 스크립트 목록
    
    class Config:
        from_attributes = True

# === MovieActor Schemas ===
class MovieActorBase(BaseModel):
    movie_id: int
    actor_id: int

class MovieActorCreate(MovieActorBase):
    pass

class MovieActor(MovieActorBase):
    actor: Optional[Actor] = None
    
    class Config:
        from_attributes = True

# === User Schemas ===
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True
