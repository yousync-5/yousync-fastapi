# routers/mypage.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from database import get_db
from dependencies import get_current_user
from models import Bookmark, Token
from schemas import BookmarkCreate, BookmarkOut, BookmarkListOut
# from schemas.user import UserProfileOut  # 이후 프로필용
# from schemas.video import DubVideoOut  # 이후 더빙 영상용
# from schemas.score import ScoreOut     # 이후 점수용

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
async def create_bookmark(
    data: BookmarkCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # 1) Token 존재 검증
    token_exists = await db.execute(
        select(Token.id).where(Token.id == data.token_id)
    )
    if not token_exists.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found",
        )

    # 2) Bookmark 삽입
    bm = Bookmark(user_id=current_user.id, token_id=data.token_id)
    db.add(bm)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        # 이미 북마크된 경우
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already bookmarked",
        )
    await db.refresh(bm)
    return bm


# --- 북마크 삭제 ---------------------------------------
@router.delete(
    "/bookmarks/{token_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_bookmark(
    token_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    res = await db.execute(
        delete(Bookmark)
        .where(
            Bookmark.user_id == current_user.id,
            Bookmark.token_id == token_id,
        )
    )
    await db.commit()
    if res.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found",
        )


# --- 북마크 목록 조회 -----------------------------------
@router.get(
    "/bookmarks/",
    response_model=List[BookmarkListOut],
)
async def list_bookmarks(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    res = await db.execute(
        select(Bookmark)
        .where(Bookmark.user_id == current_user.id)
        .options(selectinload(Bookmark.token))
        .order_by(Bookmark.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return res.scalars().all()


# --- (추후) 마이페이지 종합 정보 엔드포인트 예시 -------------
@router.get(
    "/overview",
    # response_model=MyPageOverviewOut
)
async def get_mypage_overview(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    추후에 UserProfile, 최근 N개 bookmarks, dub_videos, scores 등을
    한 번에 반환하는 엔드포인트로 확장하세요.
    """
    return {"msg": "준비 중입니다."}
