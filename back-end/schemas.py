from pydantic import BaseModel  #스키마 정의
from datetime import datetime
from typing import Optional, List

class ScriptBase(BaseModel):
    actor: str #배우이름
    start_time: float #영상 내 대사 구간(초 단위)
    end_time: float #영상 내 대사 구간(초 단위)
    script: str # 대사 원문
    translation: str# 대사  번역
    url: str # 유튜브 url
    actor_pitch_values: List[int] #배우 음성 피치 값 시계열
    background_pitch_values: List[int] # 배경음 피치 시계열

class ScriptCreate(ScriptBase): # POST /scripts/ 등에서 클라이언트가 보내는 요청 body 구조에 사용
    pass

class Script(ScriptBase): #API 서버가 클라이언트에게 응답할 때 사용하는 스키마
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True #True: SQLAlchemy ORM 객체에서 직접 변환할 수 있게 함

class MovieBase(BaseModel):
    actor: str
    total_time: int
    category: str
    url: str
    bookmark: bool = False

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
