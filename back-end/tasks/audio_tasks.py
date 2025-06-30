# tasks/audio_tasks.py
import os
import io
import requests
import logging
from uuid import uuid4
import boto3
from celery import current_task

# Celery 앱 임포트 (순환 임포트 방지)
def get_celery_app():
    from celery_app import celery_app
    return celery_app

# S3 클라이언트 설정
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "ap-northeast-2")
)

S3_BUCKET = os.getenv("S3_BUCKET_NAME")
TARGET_URL = os.getenv("TARGET_SERVER_URL", "http://43.201.26.49:8000/analyze-voice")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://yousync-fastapi-production.up.railway.app/webhook/analysis-complete")

def upload_to_s3_sync(file_data: bytes, filename: str) -> str:
    """동기적 S3 업로드"""
    try:
        key = f"audio/{uuid4().hex}_{filename}"
        s3_client.upload_fileobj(io.BytesIO(file_data), S3_BUCKET, key)
        logging.info(f"S3 업로드 완료: {key}")
        return key
    except Exception as e:
        logging.error(f"S3 업로드 실패: {e}")
        raise

@get_celery_app().task(bind=True, max_retries=3, default_retry_delay=60)
def process_audio_analysis(self, file_data: bytes, filename: str, token_id: str, job_id: str):
    """백그라운드에서 오디오 분석 처리"""
    try:
        logging.info(f"[Celery] 오디오 분석 태스크 시작 - job_id: {job_id}")
        
        # 1. 진행 상황 업데이트 (10%)
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 10,
                "status": "S3 업로드 시작",
                "job_id": job_id,
                "token_id": token_id
            }
        )
        
        # 2. S3 업로드
        s3_key = upload_to_s3_sync(file_data, filename)
        s3_url = f"s3://{S3_BUCKET}/{s3_key}"
        
        # 진행 상황 업데이트 (40%)
        self.update_state(
            state="PROGRESS", 
            meta={
                "progress": 40,
                "status": "S3 업로드 완료, 분석 서버 요청 중",
                "s3_url": s3_url,
                "job_id": job_id,
                "token_id": token_id
            }
        )
        
        # 3. 분석 서버에 요청
        webhook_url = f"{WEBHOOK_URL}?job_id={job_id}&task_id={self.request.id}"
        
        response = requests.post(
            TARGET_URL,
            data={
                "s3_audio_url": s3_url,
                "video_id": "jZOywn1qArI",  # 고정값 또는 token_id 사용
                "webhook_url": webhook_url
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"분석 서버 응답 오류: {response.status_code}")
        
        # 진행 상황 업데이트 (70%)
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 70,
                "status": "분석 서버 요청 완료, 결과 대기 중",
                "s3_url": s3_url,
                "job_id": job_id,
                "token_id": token_id
            }
        )
        
        logging.info(f"[Celery] 분석 서버 요청 완료 - job_id: {job_id}")
        
        return {
            "job_id": job_id,
            "token_id": token_id,
            "s3_url": s3_url,
            "status": "분석 요청 완료",
            "progress": 70,
            "task_id": self.request.id
        }
        
    except Exception as e:
        logging.error(f"[Celery] 태스크 실패 - job_id: {job_id}, error: {str(e)}")
        
        # 재시도 로직
        if self.request.retries < self.max_retries:
            logging.info(f"[Celery] 재시도 {self.request.retries + 1}/{self.max_retries} - job_id: {job_id}")
            raise self.retry(countdown=60, exc=e)
        
        # 최종 실패
        self.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "progress": 0,
                "job_id": job_id,
                "token_id": token_id,
                "retries": self.request.retries
            }
        )
        raise
