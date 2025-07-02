from pydantic import BaseModel, Field
from typing import Optional, List ,Any
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


# === ScriptWord ===
class ScriptWordBase(BaseModel):
    script_id: int # script_id를 기반으로 연결
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    word: Optional[str] = None
    probability: Optional[float] = None


class ScriptWord(ScriptWordBase):
    id: int

    class Config:
        from_attributes = True
 

# === Script Schemas ===
class ScriptBase(BaseModel):
    token_id: int  # ✅ 변경: token_id를 기반으로 연결
    start_time: float
    end_time: float
    script: str
    translation: Optional[str] = None


class ScriptCreate(ScriptBase):
    pass


class Script(ScriptBase):
    id: int
    # actor: Optional[Actor] = None  # 배우 정보 포함
    words: List[ScriptWord] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


# === Token Schemas ===
class TokenBase(BaseModel):
    token_name: str
    actor_name: str
    category: Optional[str] = None
    start_time: float
    end_time: float
    s3_textgrid_url: Optional[str] = None
    s3_pitch_url: Optional[str] = None
    s3_bgvoice_url: Optional[str] = None
    youtube_url: Optional[str] = None

class TokenCreate(TokenBase):
    pass

class Token(TokenBase):
    id: int
    # scripts: List[Script] = []  # 영화에 속한 스크립트 목록
    
    class Config:
        from_attributes = True

class TokenDetail(TokenBase):
    id: int
    bgvoice_url: Optional[str] = None   # presigned URL 또는 퍼블릭 URL
    pitch: Optional[Any] = None         # pitch.json 딕셔너리
    scripts: List[Script] = Field(default_factory=list)

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
