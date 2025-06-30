# router/user_audio_router.py

import os, logging, boto3, asyncio, json
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Path, HTTPException, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from concurrent.futures import ThreadPoolExecutor
import httpx

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
    prefix="/tokens",
    tags=["tokens"]
)

TARGET_URL = os.getenv("TARGET_SERVER_URL", "http://54.180.25.231:8000/analyze-voice")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://yousync-fastapi-production.up.railway.app/tokens/webhook/analysis-complete")

# 비동기 S3 업로드 함수
async def upload_to_s3_async(file_data: bytes, filename: str) -> str:
    """비동기 S3 업로드"""
    def sync_upload():
        import io
        key = f"audio/{uuid4().hex}_{filename}"
        s3.upload_fileobj(io.BytesIO(file_data), S3_BUCKET, key)
        return key
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, sync_upload)

# 비동기 HTTP 요청 함수
async def send_analysis_request_async(s3_url: str, video_id: str, webhook_url: str, job_id: str):
    """httpx를 사용한 완전 비동기 분석 요청"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                TARGET_URL,
                data={
                    "s3_audio_url": s3_url,
                    "video_id": video_id,
                    "webhook_url": webhook_url
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            logging.info(f"[분석 요청 성공] job_id={job_id}")
    except Exception as e:
        logging.error(f"[분석 요청 실패] job_id={job_id}, error={e}")

# 1. 오디오 업로드 및 분석 요청 (완전 비동기 처리)
@router.post("/{token_id}/upload-audio")
async def upload_audio_by_token_id(
    token_id: str = Path(...),
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    try:
        job_id = str(uuid4())
        file_data = await file.read()
        
        # 초기 상태 저장
        analysis_store[job_id] = {
            "status": "processing",
            "token_id": token_id,
            "progress": 10,
            "message": "업로드 시작"
        }

        # 백그라운드에서 완전 비동기 처리
        async def process_in_background():
            try:
                # S3 업로드
                analysis_store[job_id].update({
                    "progress": 40,
                    "message": "S3 업로드 중..."
                })
                
                s3_key = await upload_to_s3_async(file_data, file.filename)
                s3_url = f"s3://{S3_BUCKET}/{s3_key}"
                
                analysis_store[job_id].update({
                    "progress": 70,
                    "message": "분석 서버 요청 중...",
                    "s3_url": s3_url
                })
                
                # 비동기 분석 요청
                webhook_url = f"{WEBHOOK_URL}?job_id={job_id}"
                await send_analysis_request_async(s3_url, "jZOywn1qArI", webhook_url, job_id)
                
                analysis_store[job_id].update({
                    "progress": 90,
                    "message": "분석 중... 결과 대기"
                })
                
            except Exception as e:
                logging.error(f"백그라운드 처리 실패: {str(e)}")
                analysis_store[job_id].update({
                    "status": "failed",
                    "error": str(e),
                    "progress": 0
                })

        background_tasks.add_task(process_in_background)
        
        return {
            "message": "업로드 완료, 백그라운드에서 처리됩니다.",
            "job_id": job_id,
            "status": "processing"
        }
        
    except Exception as e:
        logging.error(f"업로드 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"에러: {str(e)}")


# 2. 분석 결과를 수신할 웹훅 엔드포인트
@router.post("/webhook/analysis-complete")
async def receive_analysis(request: Request):
    from fastapi.responses import JSONResponse
    
    job_id = request.query_params.get("job_id")
    task_id = request.query_params.get("task_id")

    if not job_id:
        logging.warning("[❗경고] job_id 없이 webhook 도착. 무시됨")
        return JSONResponse(status_code=400, content={"error": "job_id is required"})

    # 이미 완료된 job_id인지 확인
    if job_id in analysis_store:
        current_status = analysis_store[job_id].get("status")
        if current_status == "completed":
            logging.info(f"[중복 요청 무시] job_id={job_id}는 이미 완료된 상태")
            return {"received": True, "job_id": job_id, "message": "이미 완료된 작업"}

    data = await request.json()
    
    # 분석 완료 상태로 업데이트
    if job_id in analysis_store:
        analysis_store[job_id].update({
            "status": "completed",
            "progress": 100,
            "result": data,
            "message": "분석 완료"
        })
    else:
        analysis_store[job_id] = {
            "status": "completed",
            "progress": 100,
            "result": data,
            "message": "분석 완료"
        }

    logging.info(f"[분석 결과 수신] job_id={job_id}, task_id={task_id}, status={data.get('status')}")
    return {"received": True, "job_id": job_id, "task_id": task_id}


# 3. 클라이언트가 조회할 수 있는 결과 조회 API
@router.get("/analysis-result/{job_id}")
def get_analysis_result(job_id: str):
    """분석 결과 조회"""
    stored_data = analysis_store.get(job_id)
    if not stored_data:
        raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다.")
    
    return stored_data


# 4. 실시간 진행 상황을 위한 Server-Sent Events 엔드포인트
@router.get("/analysis-progress/{job_id}")
async def stream_analysis_progress(job_id: str):
    """실시간 진행 상황 스트리밍 (SSE)"""
    async def event_generator():
        stored_data = analysis_store.get(job_id)
        if not stored_data:
            yield f"data: {json.dumps({'error': 'Job not found'}, ensure_ascii=False)}\n\n"
            return
            
        while True:
            try:
                # 현재 저장된 데이터 조회
                current_data = analysis_store.get(job_id, {})
                
                # 완료된 경우 마지막 데이터 전송 후 종료
                if current_data.get("status") in ["completed", "failed"]:
                    yield f"data: {json.dumps(current_data, ensure_ascii=False)}\n\n"
                    break
                
                yield f"data: {json.dumps(current_data, ensure_ascii=False)}\n\n"
                await asyncio.sleep(1)  # 1초마다 업데이트
                
            except Exception as e:
                logging.error(f"SSE 스트림 오류: {e}")
                error_data = {
                    "status": "error", 
                    "error": str(e),
                    "job_id": job_id
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                break
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )
