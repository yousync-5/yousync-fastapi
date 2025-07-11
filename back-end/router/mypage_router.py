# routers/mypage.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from database import get_db
from router.auth_router import get_current_user
from models import Bookmark, Token, User
from schemas import BookmarkCreate, BookmarkOut, BookmarkListOut

router = APIRouter(
    prefix="/mypage", 
    tags=["MyPage"]
)


# --- 북마크 생성 ---------------------------------------
@router.post(
    "/bookmarks/",
    response_model=BookmarkOut,
    status_code=status.HTTP_201_CREATED,
)
def create_bookmark(
    data: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1) Token 존재 검증
    token_exists = db.query(Token).filter(Token.id == data.token_id).first()
    if not token_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found",
        )

    # 2) Bookmark 삽입
    bm = Bookmark(user_id=current_user.id, token_id=data.token_id)
    db.add(bm)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # 이미 북마크된 경우
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already bookmarked",
        )
    db.refresh(bm)
    return bm


# --- 북마크 삭제 ---------------------------------------
@router.delete(
    "/bookmarks/{token_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_bookmark(
    token_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookmark = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.token_id == token_id,
    ).first()
    
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found",
        )
    
    db.delete(bookmark)
    db.commit()


# --- 북마크 목록 조회 -----------------------------------
@router.get(
    "/bookmarks/",
    response_model=List[BookmarkListOut],
)
def list_bookmarks(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookmarks = (
        db.query(Bookmark)
        .filter(Bookmark.user_id == current_user.id)
        .order_by(Bookmark.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return bookmarks


# --- (추후) 마이페이지 종합 정보 엔드포인트 예시 -------------
@router.get(
    "/overview",
    # response_model=MyPageOverviewOut
)
def get_mypage_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    추후에 UserProfile, 최근 N개 bookmarks, dub_videos, scores 등을
    한 번에 반환하는 엔드포인트로 확장하세요.
    """
    return {"msg": "준비 중입니다."}


@router.delete(
    "/tokens/{token_id}/results",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="내가 더빙했던 해당 토큰의 모든 분석 결과 삭제"
)
def delete_my_token_results(
    token_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    1) 현재 로그인된 유저가 남긴 AnalysisResult 중
       token_id가 일치하는 것들을 모두 삭제합니다.
    2) 삭제된 행이 없으면 404 에러를 반환합니다.
    """
    delete_q = (
        db.query(AnalysisResult)
          .filter(AnalysisResult.user_id == current_user.id)
          .filter(AnalysisResult.token_id == token_id)
    )
    deleted_count = delete_q.delete(synchronize_session=False)
    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="삭제할 분석 결과가 없습니다."
        )
    db.commit()
    # 204 No Content이므로 반환 바디는 없습니다.
