# 영화 관련 API 엔드포인트들을 관리하는 라우터
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# 데이터베이스 관련 임포트
from database import get_db
from models import Token, Actor, MovieActor
from schemas import Token as TokenSchema, TokenCreate

# APIRouter 인스턴스 생성 - 모든 영화 관련 엔드포인트의 접두사로 "/movies" 사용
router = APIRouter(
    prefix="/tokens",   # 모든 경로 앞에 /movies가 자동으로 붙음
    tags=["tokens"]     # OpenAPI 문서에서 이 그룹의 태그명
)

# 영화 생성 API - POST 요청으로 새로운 영화 데이터를 받아 데이터베이스에 저장
@router.post("/", response_model=TokenSchema)
def create_movie(movie: TokenCreate, db: Session = Depends(get_db)):
    """
    새로운 영화를 생성합니다.
    
    - **title**: 영화 제목 (필수)
    - **category**: 장르
    - **youtube_url**: 유튜브 URL (필수)
    - **total_time**: 재생시간(분)
    """
    db_token = Token(**token.dict())  # Pydantic 모델을 SQLAlchemy 모델로 변환
    db.add(db_token)  # 데이터베이스 세션에 추가
    db.commit()  # 변경사항 커밋 (실제 DB에 저장)
    db.refresh(db_token)  # 저장된 데이터를 다시 불러와서 ID 등 업데이트
    return db_token

# 모든 영화 조회 API - 페이지네이션 지원
@router.get("/", response_model=List[MovieSchema])
def read_tokens(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    모든 영화 목록을 조회합니다.
    
    - **skip**: 건너뛸 항목 수 (기본값: 0)
    - **limit**: 가져올 최대 항목 수 (기본값: 100)
    """
    tokens = db.query(Token).offset(skip).limit(limit).all()  # SQL: SELECT * FROM movies LIMIT 100 OFFSET 0
    return tokens

# 특정 영화 조회 API - ID로 하나의 영화만 가져오기
@router.get("/{token_id}", response_model=TokenSchema)
def read_token(token_id: int, db: Session = Depends(get_db)):
    """
    특정 ID의 영화를 조회합니다.
    
    - **movie_id**: 조회할 영화의 ID
    """
    token = db.query(Token).filter(Token.id == token_id).first()  # SQL: SELECT * FROM movies WHERE id = movie_id
    if movie is None:  # 해당 ID의 영화가 없으면 404 에러 반환
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

# 영화 수정 API - PUT 요청으로 기존 영화 데이터를 업데이트
@router.put("/{movie_id}", response_model=MovieSchema)
def update_movie(movie_id: int, movie: MovieCreate, db: Session = Depends(get_db)):
    """
    기존 영화를 수정합니다.
    
    - **movie_id**: 수정할 영화의 ID
    - **title**: 수정할 영화 제목
    - **category**: 수정할 장르
    - **youtube_url**: 수정할 유튜브 URL
    """
    db_movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # 기존 영화 데이터를 새로운 데이터로 업데이트
    for field, value in movie.dict().items():
        setattr(db_movie, field, value)
    
    db.commit()  # 변경사항 저장
    db.refresh(db_movie)  # 업데이트된 데이터 다시 로드
    return db_movie

# 영화 삭제 API - DELETE 요청으로 특정 영화를 삭제
@router.delete("/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    """
    특정 ID의 영화를 삭제합니다.
    
    - **movie_id**: 삭제할 영화의 ID
    """
    db_movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    db.delete(db_movie)  # 데이터베이스에서 삭제
    db.commit()  # 변경사항 저장
    return {"detail": "Movie deleted successfully"}

# 카테고리별 영화 조회 API - 특정 카테고리의 영화들만 가져오기
@router.get("/category/{category}", response_model=List[MovieSchema])
def read_movies_by_category(category: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    특정 카테고리의 영화들을 조회합니다.
    
    - **category**: 조회할 카테고리명
    - **skip**: 건너뛸 항목 수 (기본값: 0) 
    - **limit**: 가져올 최대 항목 수 (기본값: 100)
    """
    movies = db.query(Movie).filter(Movie.category.ilike(f"%{category}%")).offset(skip).limit(limit).all()
    return movies

# 배우별 영화 조회 API - MovieActor 관계 테이블을 통해 조회
@router.get("/actor/{actor_name}", response_model=List[MovieSchema])
def read_movies_by_actor(actor_name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    특정 배우가 출연한 영화들을 조회합니다.
    
    - **actor_name**: 조회할 배우명
    - **skip**: 건너뛸 항목 수 (기본값: 0)
    - **limit**: 가져올 최대 항목 수 (기본값: 100)
    """
    # Actor 테이블에서 배우 찾기
    actor = db.query(Actor).filter(Actor.name.ilike(f"%{actor_name}%")).first()
    if not actor:
        return []
    
    # MovieActor 관계 테이블을 통해 영화 조회
    movies = db.query(Movie).join(MovieActor).filter(MovieActor.actor_id == actor.id).offset(skip).limit(limit).all()
    return movies