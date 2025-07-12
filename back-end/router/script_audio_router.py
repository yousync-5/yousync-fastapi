# router/script_audio_router.py
import os, logging, asyncio, json, io, httpx
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from fastapi import (
    APIRouter, Path, UploadFile, File, Request,
    BackgroundTasks, Depends, HTTPException
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from database import get_db, SessionLocal
from models import Script, AnalysisResult
from schemas import ScriptUser, ScriptWordUser      # ★ Pydantic 스키마

# ──────────────────────────────────────────────────
S3_BUCKET   = os.getenv("S3_BUCKET_NAME")
TARGET_URL  = os.getenv("SCRIPT_TARGET_SERVER_URL")
WEBHOOK_URL = os.getenv("SCRIPT_WEBHOOK_URL")

# ────────────── DB 헬퍼 ──────────────
def create_script_result(db: Session, job_id: str, token_id: int , user_id: int = None):

    ar = AnalysisResult(
        job_id=job_id, 
        token_id=token_id,
        user_id=user_id,
        # script_id=script_id,
        status="processing", 
        progress=10, 
        message="업로드 시작"
    )

    db.add(ar); 
    db.commit(); 
    db.refresh(ar); 
    return ar

def update_script_result(db: Session, job_id: str, **kw):
    ar = db.query(AnalysisResult).filter_by(job_id=job_id).first()
    if ar:
        for k, v in kw.items(): setattr(ar, k, v)
        db.commit(); db.refresh(ar)
    return ar

def get_script_result(db: Session, job_id: str):
    return db.query(AnalysisResult).filter_by(job_id=job_id).first()

# ────────────── ScriptUser 빌더 ──────────────
def build_script_user(db: Session, script_id: int) -> ScriptUser:
    script: Script = (
        db.query(Script)
          .options(joinedload(Script.words))
          .filter_by(id=script_id).first()
    )
    if not script:
        raise HTTPException(404, "Script not found")

    words = [
        ScriptWordUser(
            id=w.id,
            start_time=w.start_time,
            end_time=w.end_time,
            word=w.word,
            mfcc=w.mfcc        # DB에 저장돼 있던 MFCC(2-D 리스트)
        ) for w in script.words
    ]
    return ScriptUser(id=script.id, words=words)

# ────────────── 비동기 유틸 ──────────────
async def upload_to_s3_async(s3_client, file_bytes: bytes, filename: str) -> str:
    def _sync():
        key = f"audio/{uuid4().hex}_{filename}"
        s3_client.upload_fileobj(io.BytesIO(file_bytes), S3_BUCKET, key)
        return key
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as ex:
        return await loop.run_in_executor(ex, _sync)

async def send_analysis_async(s3_url: str, script_obj: ScriptUser,
                              webhook_url: str, job_id: str):
    """분석 서버로 JSON(payload) 전송"""
    payload = {
        "s3_audio_url": s3_url,
        "webhook_url":  webhook_url,
        "script":       script_obj.dict()   # Pydantic → dict
    }
    # JSON 문자열로 직렬화
    form_data = {
        "request_data": json.dumps(payload, ensure_ascii=False)
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                url=TARGET_URL,
                data=form_data,  # ★ json=X, data=O
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            resp.raise_for_status()
            logging.info(f"[분석 요청 성공] job_id={job_id}")
    except httpx.HTTPError as e:
        logging.error(f"[분석 요청 실패] job_id={job_id} - {e}")
        raise


# ────────────── Router ──────────────
router = APIRouter(prefix="/scripts", tags=["scripts"])

# 1) 업로드 + 분석 요청
@router.post("/{script_id}/upload-audio/")
async def upload_script_audio(
    request: Request,
    script_id: int = Path(...),
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):
    script = db.query(Script).filter_by(id=script_id).first()

    if not script:
        raise HTTPException(404, "Script not found")

    # ScriptUser 객체로 직렬화
    script_obj = build_script_user(db, script_id)

    # S3·분석 비동기 파이프라인
    s3_client   = request.app.state.s3_client
    job_id      = uuid4().hex
    file_bytes  = await file.read()

    create_script_result(db, job_id, token_id=script.token_id)

    async def bg_work(client_):
        bg_db = SessionLocal()
        try:
            update_script_result(bg_db, job_id, progress=40, message="S3 업로드")
            key   = await upload_to_s3_async(client_, file_bytes, file.filename)
            s3url = f"s3://{S3_BUCKET}/{key}"

            update_script_result(bg_db, job_id, progress=70, message="분석 서버 호출")
            cb    = f"{WEBHOOK_URL}?job_id={job_id}"
            await send_analysis_async(s3url, script_obj, cb, job_id)

            # 웹훅 대기 상태로 설정
            update_script_result(bg_db, job_id, progress=90, message="분석 중…")
                
        except Exception as e:
            logging.error(e)
            update_script_result(bg_db, job_id, status="failed",
                                 message=str(e), progress=0)
        finally:
            bg_db.close()

    background_tasks.add_task(bg_work, s3_client)
    return {"message": "업로드 완료, 분석 시작",
            "job_id": job_id, "status": "processing"}

# 2) 분석 서버 웹훅
@router.post("/webhook/analysis-complete/")
async def analysis_webhook(request: Request, db: Session = Depends(get_db)):
    # 웹훅 호출 로깅 추가
    logging.info("=" * 50)
    logging.info("[🔔 웹훅 호출됨] Scripts 분석 결과 웹훅 수신")
    logging.info(f"[웹훅 요청 IP] {request.client.host if request.client else 'Unknown'}")
    logging.info(f"[웹훅 헤더] {dict(request.headers)}")
    
    job_id = request.query_params.get("job_id")
    logging.info(f"[웹훅 파라미터] job_id={job_id}")
    
    if not job_id:
        logging.warning("[❗경고] Scripts 웹훅에 job_id 없음")
        raise HTTPException(400, "job_id missing")
        
    payload = await request.json()
    logging.info(f"[웹훅 데이터] 받은 결과 크기: {len(str(payload))} 문자")
    logging.info(f"[웹훅 데이터] 결과 키들: {list(payload.keys()) if isinstance(payload, dict) else 'Not dict'}")
    
    update_script_result(db, job_id, status="completed",
                         progress=100, result=payload, message="분석 완료")
    
    logging.info(f"[✅ 웹훅 처리 완료] job_id={job_id}")
    logging.info("=" * 50)
    return {"received": True, "job_id": job_id}

# 3) 결과 조회
@router.get("/analysis-result/{job_id}/")
def get_result(job_id: str, db: Session = Depends(get_db)):
    r = get_script_result(db, job_id)
    if not r:
        raise HTTPException(404, "결과가 없습니다.")
    return {
        "job_id":    r.job_id,
        "token_id":  r.token_id,   # script_id 필드 제거
        # "script_id": r.script_id,
        "status":    r.status,
        "progress":  r.progress,
        "result":    r.result,
        "message":   r.message,
        "created_at": r.created_at,
    }

# 4) SSE 진행 스트림
@router.get("/analysis-progress/{job_id}/")
async def stream_progress(job_id: str):
    async def gen():
        while True:
            db = SessionLocal()
            try:
                r = get_script_result(db, job_id)
                if not r:
                    yield "data: {\"error\":\"Job not found\"}\n\n"
                    break
                data = {
                    "job_id":   r.job_id,
                    "status":   r.status,
                    "progress": r.progress,
                    "message":  r.message,
                    "result":   r.result,
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                if r.status in ("completed", "failed"): break
            finally:
                db.close()
            await asyncio.sleep(1)
    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control":"no-cache",
                                      "Connection":"keep-alive",
                                      "Access-Control-Allow-Origin":"*"})
