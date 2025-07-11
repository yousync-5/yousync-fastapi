# routers/mypage.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, func, desc

from database import get_db
from router.auth_router import get_current_user
from models import Bookmark, Token, User, AnalysisResult, Script
from schemas import BookmarkCreate, BookmarkOut, BookmarkListOut, MyDubbedTokenResponse, TokenAnalysisStatusResponse

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


@router.get(
    "/my-dubbed-tokens",
    response_model=List[MyDubbedTokenResponse],
    summary="내가 더빙한 토큰 목록 조회"
)
def get_my_dubbed_tokens(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    현재 로그인한 유저가 더빙한 토큰들의 목록을 반환합니다.
    각 토큰별로 마지막 더빙 시간, 전체 스크립트 수, 완료된 스크립트 수를 포함합니다.
    """
    # 내가 더빙한 토큰들 조회 (서브쿼리 사용)
    subquery = (
        db.query(
            Token.id.label('token_id'),
            Token.token_name,
            Token.actor_name, 
            Token.category,
            func.max(AnalysisResult.created_at).label('last_dubbed_at'),
            func.count(Script.id).label('total_scripts'),
            func.count(AnalysisResult.id).label('completed_scripts')
        )
        .join(Script, Script.token_id == Token.id)
        .join(AnalysisResult, AnalysisResult.script_id == Script.id)
        .filter(AnalysisResult.user_id == current_user.id)
        .group_by(Token.id, Token.token_name, Token.actor_name, Token.category)
        .order_by(desc('last_dubbed_at'))
        .limit(limit)
        .offset(offset)
        .all()
    )
    
    # 결과 변환
    results = []
    for row in subquery:
        results.append(MyDubbedTokenResponse(
            token_id=row.token_id,
            token_name=row.token_name,
            actor_name=row.actor_name,
            category=row.category,
            last_dubbed_at=row.last_dubbed_at,
            total_scripts=row.total_scripts,
            completed_scripts=row.completed_scripts
        ))
    
    return results


@router.get(
    "/tokens/{token_id}/analysis-status",
    response_model=TokenAnalysisStatusResponse,
    summary="특정 토큰의 내 분석 상태 확인"
)
def get_token_analysis_status(
    token_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    특정 토큰에 대한 현재 유저의 분석 결과 존재 여부와 상세 정보를 반환합니다.
    더빙 기록이 있으면 결과창으로, 없으면 더빙 시작 화면으로 분기하는데 사용됩니다.
    """
    # 해당 토큰의 스크립트들과 내 분석 결과 조회
    results = (
        db.query(Script, AnalysisResult)
        .outerjoin(AnalysisResult, 
                  (AnalysisResult.script_id == Script.id) & 
                  (AnalysisResult.user_id == current_user.id))
        .filter(Script.token_id == token_id)
        .all()
    )
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    # 분석 결과 정리
    script_results = []
    has_any_analysis = False
    
    for script, analysis in results:
        if analysis:
            has_any_analysis = True
            script_results.append({
                "script_id": script.id,
                "script_text": script.script,
                "has_result": True,
                "job_id": analysis.job_id,
                "status": analysis.status,
                "result": analysis.result,
                "created_at": analysis.created_at
            })
        else:
            script_results.append({
                "script_id": script.id,
                "script_text": script.script,
                "has_result": False
            })
    
    return TokenAnalysisStatusResponse(
        token_id=token_id,
        has_analysis=has_any_analysis,
        script_results=script_results
    )


@router.delete(
    "/tokens/{token_id}/my-results",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="재더빙을 위한 기존 분석 결과 삭제"
)
def delete_my_token_results(
    token_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    재더빙 시 해당 토큰의 모든 기존 분석 결과를 삭제합니다.
    한 유저당 동일 토큰의 분석결과는 1세트만 존재하도록 보장합니다.
    """
    # 해당 토큰의 스크립트 ID들 조회
    script_ids = db.query(Script.id).filter(Script.token_id == token_id).all()
    script_id_list = [sid[0] for sid in script_ids]
    
    if not script_id_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    # 내 분석 결과들 삭제
    deleted_count = (
        db.query(AnalysisResult)
        .filter(
            AnalysisResult.script_id.in_(script_id_list),
            AnalysisResult.user_id == current_user.id
        )
        .delete(synchronize_session=False)
    )
    
    db.commit()
    
    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="삭제할 분석 결과가 없습니다."
        )


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
