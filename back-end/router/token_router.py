# 영화 관련 API 엔드포인트들을 관리하는 라우터
from fastapi import APIRouter, Depends, HTTPException, Path, Request
from sqlalchemy import update
from sqlalchemy.orm import Session
from typing import List

# 데이터베이스 관련 임포트
from database import get_db
from models import Token, Actor, TokenActor
from schemas import Token as TokenSchema
from schemas import TokenCreate,TokenDetail, ViewCountResponse
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

@router.get("/popular", response_model=List[TokenSchema])
def read_popular_tokens(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    조회수가 높은 토큰 목록을 조회한다.
    - **skip**: 건너뛸 항목 수 (기본값: 0)
    - **limit**: 가져올 최대 항목 수 (기본값: 100)
    """
    tokens = db.query(Token).order_by(Token.view_count.desc()).offset(skip).limit(limit).all()
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


# 모달용 Token_id to actor_token 
@router.get("/{token_id}/related", response_model = List[TokenSchema])
def read_related_tokens(token_id: int, skip: int = 0, limit: int = 5, db: Session = Depends(get_db)):
    """
    모달용
    Token_id 를 받아 해당 actor의 Token들을 반환한다.
    """
    token = db.get(Token, token_id)
    if not token: 
        raise HTTPException(status_code=404, detail="Token not found")
    
    # 기준 토큰  -> actor_id
    actor_id = (db.query(TokenActor.actor_id).filter(TokenActor.token_id == token_id).scalar())

    if actor_id is None:
        raise HTTPException(status_code=404, detail="해당 토큰과 연결된 배우를 찾을 수 없습니다.")
    

    # 3) 같은 배우의 다른 토큰들 조회 (JOIN + 페이징 + 정렬)
    related = (
        db.query(Token)
          .join(TokenActor, Token.id == TokenActor.token_id)
          .filter(TokenActor.actor_id == actor_id,
                  Token.id != token_id)
          .order_by(Token.view_count.desc())
          .offset(skip)
          .limit(limit)
          .all()
    )
    
    return related


# token 조회수 상승 API
@router.post("/{token_id}/view", response_model=ViewCountResponse)
def increment_view(token_id: int, db: Session = Depends(get_db)):
    token = db.query(Token).filter(Token.id == token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    # DB 레벨에서 atomic 하게 view_count += 1
    stmt = (
        update(Token)
        .where(Token.id == token_id)
        .values(view_count = Token.view_count + 1)
        .execution_options(synchronize_session="fetch")
    )
    try: 
        db.execute(stmt)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(500, "조회수 증가 중 오류가 발생")

    token = db.get(Token, token_id)
    return {"token_id": token.id, "view_count": token.view_count}


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
