# app/routers/score_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import AnalysisResult, User
from schemas import TokenScore
from router.auth_router import get_current_user


router = APIRouter(prefix="/score", tags=["score"])


@router.get(
    "/{token_id}/score",
    response_model=TokenScore,
    summary="내가 등록한 토큰의 평균 Token_score 조회"
)
def get_my_token_score(
    token_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TokenScore:
    # 내가 올린 분석 결과만 골라서 평균 계산
    stmt = (
        select(func.avg(
            (AnalysisResult.result["result"]["overall_score"]).as_float()
        ))
        .where(AnalysisResult.token_id == token_id)
        .where(AnalysisResult.user_id == current_user.id)
    )
    avg_score: Optional[float] = db.execute(stmt).scalar()
    if avg_score is None:
        raise HTTPException(status_code=404, detail="조회 가능한 결과가 없습니다.")
    return TokenScore(
        token_id=token_id,
        average_score=round(avg_score, 2)
    )


@router.get(
    "/me/average_score",
    response_model=UserScore,
    summary="내가 등록한 모든 더빙 결과의 전체 평균 점수 조회"
)
def get_my_overall_average_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserAverageScore:
    # 1) current_user.id 로 필터
    # 2) result JSON 내부의 overall_score를 float 로 꺼내 평균 계산
    stmt = (
        select(func.avg(
            (AnalysisResult.result["result"]["overall_score"]).as_float()
        ))
        .where(AnalysisResult.user_id == current_user.id)
    )
    avg_score: Optional[float] = db.execute(stmt).scalar()

    if avg_score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="더빙 결과가 없습니다."
        )

    return UserScore(
        user_id=current_user.id,
        average_score=round(avg_score, 2)
    )


@router.get(
    "/me/tokens/full",
    response_model=UserToken,
    summary="내가 등록한 모든 토큰(full) 조회"
)
def get_my_full_tokens(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserToken:
    # 1) 내가 사용한 토큰 ID만 distinct 하게 조회
    subq = (
        select(AnalysisResult.token_id)
        .where(AnalysisResult.user_id == current_user.id)
        .distinct()
        .subquery()
    )
    # 2) TokenModel 전체 객체 조회
    tokens = db.query(TokenModel).join(subq, TokenModel.id == subq.c.token_id).all()

    return UserToken(
        user_id=current_user.id,
        tokens=tokens
    )

