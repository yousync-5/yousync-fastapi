# 배우 관련 API 엔드포인트들을 관리하는 라우터
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from typing import List

# 데이터베이스 관련 임포트
from database import get_db
from models import Token, Actor, TokenActor, ActorAlias
from schemas import Actor as ActorSchema, ActorCreate
from schemas import Token as TokenSchema

# APIRouter 인스턴스 생성
router = APIRouter(
    prefix="/actors",
    tags=["actors"]
)

# 배우 생성 API
@router.post("/", response_model=ActorSchema)
def create_actor(actor: ActorCreate, db: Session = Depends(get_db)):
    """
    새로운 배우를 생성합니다.
    
    - **name**: 배우 이름 (필수, 고유값)
    """
    # 같은 이름의 배우가 이미 있는지 확인
    existing_actor = db.query(Actor).filter(Actor.name == actor.name).first()
    if existing_actor:
        raise HTTPException(status_code=400, detail="Actor already exists")
    
    db_actor = Actor(**actor.dict())
    db.add(db_actor)
    db.commit()
    db.refresh(db_actor)
    return db_actor

# 모든 배우 조회 API
@router.get("/", response_model=List[ActorSchema])
def read_actors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    모든 배우 목록을 조회합니다.
    
    - **skip**: 건너뛸 항목 수 (기본값: 0)
    - **limit**: 가져올 최대 항목 수 (기본값: 100)
    """
    actors = db.query(Actor).offset(skip).limit(limit).all()
    return actors


# 배우별 영화 조회 API - TokenActor 관계 테이블을 통해 조회
SIM_TH = 0.25                # 유사도 임계값 조정 가능

@router.get("/{query}", response_model=List[TokenSchema])
def read_tokens_by_actor(
    query: str,
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    배우별 영화 조회, 검색용(영어, 한글 가능)
    """
    q = query.strip()
    if not q:
        return []

    # ── 1) 별칭 테이블 1차 매치 (부분 일치, 대소문자·한영 모두)
    alias_rows = (
        db.query(ActorAlias.actor_id)
          .filter(ActorAlias.name.ilike(f"%{q}%"))
          .limit(10)
          .all()
    )
    actor_ids = [row[0] for row in alias_rows]

    # ── 2) 오타 보정 매치 (pg_trgm)
    if len(actor_ids) < 10:
        extra = (
            db.query(ActorAlias.actor_id)
              .filter(func.similarity(ActorAlias.name, q) > SIM_TH)
              .order_by(desc(func.similarity(ActorAlias.name, q)))
              .limit(10 - len(actor_ids))
              .all()
        )
        actor_ids.extend(row[0] for row in extra)

    if not actor_ids:
        return []

    # ── 3) 토큰 조회
    tokens = (
        db.query(Token)
          .join(TokenActor, TokenActor.token_id == Token.id)
          .filter(TokenActor.actor_id.in_(actor_ids))
          .offset(skip).limit(limit)
          .all()
    )
    return tokens



# # 배우 수정 API
# @router.put("/{actor_id}", response_model=ActorSchema)
# def update_actor(actor_id: int, actor: ActorCreate, db: Session = Depends(get_db)):
#     """
#     기존 배우 정보를 수정합니다.
    
#     - **actor_id**: 수정할 배우의 ID
#     - **name**: 수정할 배우 이름
#     """
#     db_actor = db.query(Actor).filter(Actor.id == actor_id).first()
#     if db_actor is None:
#         raise HTTPException(status_code=404, detail="Actor not found")
    
#     # 이름 중복 체크 (자기 자신 제외)
#     if actor.name != db_actor.name:
#         existing_actor = db.query(Actor).filter(Actor.name == actor.name).first()
#         if existing_actor:
#             raise HTTPException(status_code=400, detail="Actor name already exists")
    
#     for field, value in actor.dict().items():
#         setattr(db_actor, field, value)
    
#     db.commit()
#     db.refresh(db_actor)
#     return db_actor

# # 배우 삭제 API
# @router.delete("/{actor_id}")
# def delete_actor(actor_id: int, db: Session = Depends(get_db)):
#     """
#     특정 ID의 배우를 삭제합니다.
    
#     - **actor_id**: 삭제할 배우의 ID
#     """
#     db_actor = db.query(Actor).filter(Actor.id == actor_id).first()
#     if db_actor is None:
#         raise HTTPException(status_code=404, detail="Actor not found")
    
#     db.delete(db_actor)
#     db.commit()
#     return {"detail": "Actor deleted successfully"}
