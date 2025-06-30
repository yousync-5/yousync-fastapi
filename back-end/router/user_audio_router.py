# router/user_audio_router.py

import os, shutil, requests, logging, boto3, asyncio, json
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Path, HTTPException, Request
from fastapi.responses import StreamingResponse
from celery.result import AsyncResult
from tasks.audio_tasks import process_audio_analysis
from celery_app import celery_app

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

TARGET_URL = os.getenv("TARGET_SERVER_URL", "http://43.201.26.49:8000/analyze-voice")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://yousync-fastapi-production.up.railway.app/webhook/analysis-complete")

# 1. 오디오 업로드 및 분석 요청 (Celery로 최적화)
@router.post("/{token_id}/upload-audio")
async def upload_audio_by_token_id(
    token_id: str = Path(...),
    file: UploadFile = File(...)
):
    try:
        job_id = str(uuid4())
        
        # 파일 데이터를 메모리에서 읽기
        file_data = await file.read()
        
        # 초기 상태 저장 (즉시 응답을 위해)
        analysis_store[job_id] = {
            "status": "queued",
            "token_id": token_id,
            "progress": 0,
            "message": "분석 큐에 추가됨"
        }
        
        # Celery 태스크 시작 (백그라운드 처리)
        task = process_audio_analysis.delay(
            file_data, 
            file.filename, 
            token_id, 
            job_id
        )
        
        # 태스크 ID 저장
        analysis_store[job_id]["task_id"] = task.id
        
        logging.info(f"[Celery] 태스크 시작 - job_id: {job_id}, task_id: {task.id}")
        
        # 즉시 응답 반환 (사용자는 더 이상 기다리지 않음)
        return {
            "message": "업로드 완료, 분석이 백그라운드에서 진행됩니다.",
            "job_id": job_id,
            "task_id": task.id,
            "status": "queued"
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
            "result": data
        }

    logging.info(f"[분석 결과 수신] job_id={job_id}, task_id={task_id}, status={data.get('status')}")
    return {"received": True, "job_id": job_id, "task_id": task_id}


# 3. 클라이언트가 조회할 수 있는 결과 조회 API (실시간 진행 상황 포함)
@router.get("/analysis-result/{job_id}")
def get_analysis_result(job_id: str):
    """분석 결과 조회 (Celery 태스크 상태 포함)"""
    stored_data = analysis_store.get(job_id)
    if not stored_data:
        raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다.")
    
    task_id = stored_data.get("task_id")
    if task_id:
        try:
            # Celery 태스크 상태 확인
            result = AsyncResult(task_id, app=celery_app)
            
            if result.state == "PENDING":
                return {
                    **stored_data,
                    "status": "queued",
                    "progress": 0,
                    "message": "분석 대기 중..."
                }
            elif result.state == "PROGRESS":
                task_info = result.info or {}
                return {
                    **stored_data,
                    "status": "processing",
                    "progress": task_info.get("progress", 0),
                    "message": task_info.get("status", "처리 중..."),
                    "s3_url": task_info.get("s3_url")
                }
            elif result.state == "SUCCESS":
                task_result = result.result or {}
                return {
                    **stored_data,
                    "status": "awaiting_webhook",  # 분석 서버 작업 완료, 웹훅 대기
                    "progress": task_result.get("progress", 70),
                    "message": "분석 서버 처리 완료, 결과 대기 중...",
                    "task_result": task_result
                }
            elif result.state == "FAILURE":
                error_info = result.info or {}
                return {
                    **stored_data,
                    "status": "failed",
                    "progress": 0,
                    "error": str(error_info.get("error", result.info)),
                    "retries": error_info.get("retries", 0)
                }
        except Exception as e:
            logging.error(f"Celery 결과 조회 실패: {e}")
    
    # 기본 저장된 데이터 반환
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
            
        task_id = stored_data.get("task_id")
        
        while True:
            try:
                if task_id:
                    result = AsyncResult(task_id, app=celery_app)
                    
                    if result.state == "PENDING":
                        data = {
                            **stored_data,
                            "status": "queued",
                            "progress": 0,
                            "message": "분석 대기 중..."
                        }
                    elif result.state == "PROGRESS":
                        task_info = result.info or {}
                        data = {
                            **stored_data,
                            "status": "processing",
                            "progress": task_info.get("progress", 0),
                            "message": task_info.get("status", "처리 중..."),
                            "s3_url": task_info.get("s3_url")
                        }
                    elif result.state == "SUCCESS":
                        task_result = result.result or {}
                        data = {
                            **stored_data,
                            "status": "awaiting_webhook",
                            "progress": task_result.get("progress", 70),
                            "message": "분석 서버 처리 완료, 결과 대기 중...",
                            "task_result": task_result
                        }
                    elif result.state == "FAILURE":
                        error_info = result.info or {}
                        data = {
                            **stored_data,
                            "status": "failed",
                            "progress": 0,
                            "error": str(error_info.get("error", result.info))
                        }
                        yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                        break
                    else:
                        data = stored_data
                else:
                    data = stored_data
                
                # 최종 완료 확인 (웹훅으로 완료된 경우)
                current_stored = analysis_store.get(job_id, {})
                if current_stored.get("status") == "completed":
                    data = current_stored
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                    break
                
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                
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
