from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from router.auth_router import get_current_user
from router.utils_s3 import load_main_audio_from_s3
from utils.synthesize import (
    get_token_info,
    get_scripts_by_token,
    prepare_dub_segments,
    synthesize_audio_from_segments
)

router = APIRouter(tags=["synthesize"])

@router.post("/synthesize/{token_id}")
def synthesize_audio_endpoint(
    token_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_id = current_user.id

    # 1. 토큰 정보 가져오기
    actor_name, video_id, token_start_time = get_token_info(db, token_id)

    # 2. 배경 + 원본 음성 로딩
    background, original = load_main_audio_from_s3(actor_name, video_id)

    # 3. 스크립트와 더빙 음성 로딩
    scripts = get_scripts_by_token(db, token_id)
    segments = prepare_dub_segments(user_id, token_id, scripts, token_start_time)

    if not segments:
        raise HTTPException(status_code=404, detail="사용자 더빙 음성이 없습니다.")

    # 4. 합성 실행
    output_path = f"final_mix_{token_id}_{user_id}.wav"
    synthesize_audio_from_segments(background, original, segments, output_path)

    return {
        "status": "success",
        "message": "합성 완료",
        "output": output_path  # 또는 S3 업로드 후 presigned URL
    }
