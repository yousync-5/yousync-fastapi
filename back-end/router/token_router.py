# 영화 관련 API 엔드포인트들을 관리하는 라우터
from fastapi import APIRouter, Depends, HTTPException,Path, Request
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from typing import List

# 데이터베이스 관련 임포트
from database import get_db
from models import Token, Actor, TokenActor, ActorAlias
from schemas import Token as TokenSchema
from schemas import TokenCreate,TokenDetail
from .utils_s3 import load_json, presign

# APIRouter 인스턴스 생성 - 모든 영화 관련 엔드포인트의 접두사로 "/movies" 사용
router = APIRouter(
    prefix="/tokens",   # 모든 경로 앞에 /movies가 자동으로 붙음
    tags=["tokens"]     # OpenAPI 문서에서 이 그룹의 태그명
)

# 영화 생성 API - POST 요청으로 새로운 영화 데이터를 받아 데이터베이스에 저장
@router.post("/", response_model=TokenSchema)
def create_token(token: TokenCreate, db: Session = Depends(get_db)):
    """
    새로운 토큰을 생성합니다.
    """
    db_token = Token(**token.dict())  # Pydantic 모델을 SQLAlchemy 모델로 변환
    db.add(db_token)  # 데이터베이스 세션에 추가
    db.commit()  # 변경사항 커밋 (실제 DB에 저장)
    db.refresh(db_token)  # 저장된 데이터를 다시 불러와서 ID 등 업데이트
    return db_token

# 모든 영화 조회 API - 페이지네이션 지원
@router.get("/", response_model=List[TokenSchema])
def read_tokens(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    모든 토큰 목록을 조회합니다.
    
    - **skip**: 건너뛸 항목 수 (기본값: 0)
    - **limit**: 가져올 최대 항목 수 (기본값: 100)
    """
    tokens = db.query(Token).offset(skip).limit(limit).all()  # SQL: SELECT * FROM movies LIMIT 100 OFFSET 0
    return tokens


@router.get("/{token_id}", response_model=TokenDetail)
async def read_token(
    request: Request,
    token_id: int = Path(...),
    db: Session = Depends(get_db)
):
    """
    토큰 + scripts + pitch.json + bgvoice presigned URL
    """
    s3_client = request.app.state.s3_client
    token: Token | None = db.query(Token).filter(Token.id == token_id).first()
    if token is None:
        raise HTTPException(404, "Token not found")

    pitch_data   = await load_json(s3_client, token.s3_pitch_url)
    safe_bgvoice = presign(s3_client, token.s3_bgvoice_url)   # 퍼블릭이면 그대로

    # SQLAlchemy 객체 dict 언패킹 + 추가 필드
    return TokenDetail(
        **token.__dict__,
        scripts=[*token.scripts],    # relationship 로드
        pitch=pitch_data,
        bgvoice_url=safe_bgvoice
    )

# 영화 수정 API - PUT 요청으로 기존 영화 데이터를 업데이트
@router.put("/{token_id}", response_model=TokenSchema)
def update_token(token_id: int, token: TokenCreate, db: Session = Depends(get_db)):
    """
    기존 토큰을 수정합니다.
    """
    db_token = db.query(Token).filter(Token.id == token_id).first()
    if db_token is None:
        raise HTTPException(status_code=404, detail="Token not found")
    
    # 기존 영화 데이터를 새로운 데이터로 업데이트
    for field, value in token.dict().items():
        setattr(db_token, field, value)
    
    db.commit()  # 변경사항 저장
    db.refresh(db_token)  # 업데이트된 데이터 다시 로드
    return db_token

# 영화 삭제 API - DELETE 요청으로 특정 영화를 삭제
@router.delete("/{token_id}")
def delete_token(token_id: int, db: Session = Depends(get_db)):
    """
    특정 ID의 토큰를 삭제합니다.
    """
    db_token = db.query(Token).filter(Token.id == token_id).first()
    if db_token is None:
        raise HTTPException(status_code=404, detail="Token not found")
    
    db.delete(db_token)  # 데이터베이스에서 삭제
    db.commit()  # 변경사항 저장
    return {"detail": "Token deleted successfully"}

# 카테고리별 영화 조회 API - 특정 카테고리의 영화들만 가져오기
# @router.get("/category/{category}", response_model=List[TokenSchema])
# def read_tokens_by_category(category: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     """
#     특정 카테고리의 토큰들을 조회합니다.
    
#     - **category**: 조회할 카테고리명
#     - **skip**: 건너뛸 항목 수 (기본값: 0) 
#     - **limit**: 가져올 최대 항목 수 (기본값: 100)
#     """
#     tokens = db.query(Token).filter(Token.category.ilike(f"%{category}%")).offset(skip).limit(limit).all()
#     return tokens


# 배우별 영화 조회 API - TokenActor 관계 테이블을 통해 조회
SIM_TH = 0.25                # 유사도 임계값 조정 가능

@router.get("/actor/{query}", response_model=List[TokenSchema])
def read_tokens_by_actor(
    query: str,
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db)
):
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