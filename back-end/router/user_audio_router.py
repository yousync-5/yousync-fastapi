# router/user_audio_router.py

import os, shutil, requests, logging, boto3
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Path, HTTPException, Request

# 간단한 메모리 저장소 (프로덕션에서는 DB로 교체 권장)
analysis_store = {}

# boto3로 업로드 함수 구현, 추후 분리 가능 boto3를 import
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

S3_BUCKET = os.getenv("S3_BUCKET_NAME")

def upload_to_s3(file, filename) -> str:
    key = f"audio/{uuid4().hex}_{filename}"
    s3.upload_fileobj(file, S3_BUCKET, key)
    return key
# ===============================================

router = APIRouter(
    prefix="/movies",
    tags=["movies"]
)

TARGET_URL = os.getenv("TARGET_SERVER_URL", "http://43.201.26.49:8000/analyze-voice")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://yousync-fastapi-production.up.railway.app/webhook/analysis-complete")

# 1. 오디오 업로드 및 분석 요청
@router.post("/{movie_id}/upload-audio")
async def upload_audio_by_movie_id(
    movie_id: str = Path(...),
    file: UploadFile = File(...)
):
    try:
        s3_key = upload_to_s3(file.file, file.filename)
        s3_url = f"s3://{S3_BUCKET}/{s3_key}"
        job_id = str(uuid4())
        webhook_url = f"{WEBHOOK_URL}?job_id={job_id}"

        # 분석 요청
        try:
            response = requests.post(
                TARGET_URL,
                data={
                    "s3_audio_url": s3_url,
                    "video_id": movie_id,
                    "webhook_url": webhook_url
                },
                headers={
                    # "ngrok-skip-browser-warning": "true",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
            )
            response.raise_for_status()
        except Exception as e:
            logging.error(f"[분석 요청 실패] job_id={job_id}, error={e}")

        # 상태 저장
        analysis_store[job_id] = {
            "status": "processing",
            "s3_audio_url": s3_url,
            "video_id": movie_id
        }

        return {
            "message": "분석 요청을 보냈습니다.",
            "job_id": job_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"에러: {str(e)}")


# 2. 분석 결과를 수신할 웹훅 엔드포인트
@router.post("/webhook/analysis-complete")
async def receive_analysis(request: Request):
    job_id = request.query_params.get("job_id")

    if not job_id:
        logging.warning("[❗경고] job_id 없이 webhook 도착. 무시됨")
        return JSONResponse(status_code=400, content={"error": "job_id is required"})

    data = await request.json()
    analysis_store[job_id] = data

    logging.info(f"[분석 결과 수신] job_id={job_id}, status={data.get('status')}")
    return {"received": True, "job_id": job_id}


# 3. 클라이언트가 조회할 수 있는 결과 조회 API
@router.get("/analysis-result/{job_id}")
def get_analysis_result(job_id: str):
    result = analysis_store.get(job_id)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다.")
