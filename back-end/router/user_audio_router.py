# router/user_audio_router.py

import os, shutil, requests, logging
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Path, HTTPException

# router = APIRouter()

router = APIRouter(
    prefix="/movies",
    tags=["movies"]
)

TARGET_URL = os.getenv("TARGET_SERVER_URL", "https://target-server.com/receive")

# @router.post("/movies/{movie_id}/upload-audio")
@router.post("/{movie_id}/upload-audio")
async def upload_audio_by_movie_id(
    movie_id: str = Path(..., description="업로드할 영화의 ID"),
    file: UploadFile = File(...)
):
    filename = f"{uuid4().hex}_{file.filename}"
    file_path = f"temp/{filename}"
    os.makedirs("temp", exist_ok=True)
    os.makedirs("failed_uploads", exist_ok=True)

    try:
        # 1. 파일 임시 저장
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. 분석 서버에 요청
        with open(file_path, "rb") as f:
            mime = file.content_type or "application/octet-stream"
            response = requests.post(
                TARGET_URL,
                files={"file": (filename, f, mime)},
                data={"movie_id": movie_id},
                timeout=15
            )
        
        # 3. 응답 확인 및 JSON 파싱
        response.raise_for_status()
        analysis_result = response.json()

        logging.info(f"[전송 성공] movie_id={movie_id}, result={analysis_result}")
        
        # 4. 클라이언트에게 분석 결과 전달
        return {
            "message": "분석 완료",
            "movie_id": movie_id,
            "filename": filename,
            "analysis_result": analysis_result
        }

    except Exception as e:
        logging.error(f"[전송 실패] movie_id={movie_id}, 오류: {e}")
        shutil.move(file_path, f"failed_uploads/{filename}")
        raise HTTPException(status_code=500, detail=f"분석 서버와의 통신 실패: {str(e)}")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
