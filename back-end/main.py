"""
FastAPI 영화/스크립트 관리 API 서버

이 애플리케이션은 영화와 스크립트 데이터를 관리하는 REST API 서버입니다.
PostgreSQL 데이터베이스를 사용하여 데이터를 저장하고 관리합니다.

주요 기능:
- 스크립트 CRUD 작업 (생성, 조회, 수정, 삭제)
- 영화 CRUD 작업 (생성, 조회, 수정, 삭제)
- 장르별/감독별 영화 검색
- API 문서 자동 생성 (Swagger UI)

API 문서 접근:
- Swagger UI: https://yousync-fastapi-production.up.railway.app/docs
- ReDoc: https://yousync-fastapi-production.up.railway.app/redoc
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 데이터베이스 관련 임포트
from database import engine
from models import Base

# 라우터 임포트 - 각 도메인별로 분리된 API 엔드포인트들
from router.script_router import router as script_router
from router.token_router import router as token_router
# from router.actor_router import router as actor_router

# user_audio_router는 Celery 의존성이 있으므로 안전하게 임포트
try:
    from router.user_audio_router import router as user_audio_router
    USER_AUDIO_AVAILABLE = True
except ImportError as e:
    print(f"user_audio_router 임포트 실패: {e}")
    USER_AUDIO_AVAILABLE = False

# 데이터베이스 테이블 생성 (앱 시작시 자동으로 테이블이 생성됨)
Base.metadata.create_all(bind=engine)

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title="영화/스크립트 관리 API",
    description="영화와 스크립트 데이터를 관리하는 REST API 서버입니다.",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI 경로
    redoc_url="/redoc"     # ReDoc 경로
)

#정적 파일 mount
app.mount("/media", StaticFiles(directory="media"), name="media") 

# CORS 미들웨어 설정 - 프론트엔드에서 API 호출을 허용하기 위함
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 모든 도메인에서의 접근 허용 (프로덕션에서는 특정 도메인만 허용하는 것이 보안상 좋음)
    allow_credentials=True,     # 쿠키/인증 정보 포함한 요청 허용
    allow_methods=["*"],        # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],        # 모든 헤더 허용
)

# API 라우터 등록 - 각 도메인별로 분리된 엔드포인트들을 메인 앱에 연결
app.include_router(script_router)  # /scripts 경로로 스크립트 관련 API 등록
app.include_router(token_router)   # /tokens 경로로 토큰 관련 API 등록
# app.include_router(actor_router)   # /actors 경로로 배우 관련 API 등록

if USER_AUDIO_AVAILABLE:
    app.include_router(user_audio_router) # /tokens/{token_id}/upload-audio 경로로 유저 음성 데이터 관련 API 등록

# 루트 엔드포인트 - API 서버 상태 확인용
@app.get("/")
def read_root():
    """
    API 서버 상태를 확인하는 루트 엔드포인트입니다.
    서버가 정상적으로 작동하는지 확인할 때 사용합니다.
    """
    return {
        "message": "토큰/스크립트 관리 API 서버가 정상적으로 작동중입니다!",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "1.0.0"
    }

# Health Check 엔드포인트 - 서버 상태 모니터링용
@app.get("/health")
def health_check():
    """
    서버 상태를 체크하는 헬스체크 엔드포인트입니다.
    로드밸런서나 모니터링 도구에서 서버 상태를 확인할 때 사용합니다.
    """
    return {"status": "healthy", "service": "token-script-api"}