# celery_app.py
from celery import Celery
import os

# Redis를 브로커로 사용 (로컬 개발시에는 redis://localhost:6379/0 사용)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "yousync_voice_analysis",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks.audio_tasks"]  # 태스크 모듈 포함
)

# Celery 설정
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,
    
    # 태스크 라우팅
    task_routes={
        "tasks.audio_tasks.process_audio_analysis": {"queue": "audio_queue"}
    },
    
    # 재시도 설정
    task_default_retry_delay=60,  # 60초 후 재시도
    task_max_retries=3,
    
    # 결과 만료 시간
    result_expires=3600,  # 1시간 후 결과 삭제
)

if __name__ == "__main__":
    celery_app.start()
