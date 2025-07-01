# FastAPI 오디오 분석 서비스

FastAPI와 httpx를 활용한 완전 비동기 오디오 분석 백엔드 서비스입니다. 
기존 Celery/Redis 기반 처리를 httpx 기반 비동기 처리로 완전히 리팩토링하여 더 가볍고 효율적인 구조로 개선되었습니다.

## 🚀 주요 특징

- **완전 비동기 처리**: httpx와 FastAPI BackgroundTasks를 활용한 논블로킹 처리
- **S3 비동기 업로드**: ThreadPoolExecutor를 통한 S3 파일 업로드 최적화
- **실시간 진행 상황**: Server-Sent Events(SSE)를 통한 실시간 진행률 추적
- **가벼운 아키텍처**: Celery/Redis 의존성 제거로 단순화된 구조
- **RESTful API**: 직관적인 API 엔드포인트 설계

## 📁 프로젝트 구조

```
fast-api/
├── back-end/
│   ├── main.py                 # FastAPI 애플리케이션 진입점
│   ├── models.py              # 데이터베이스 모델
│   ├── schemas.py             # Pydantic 스키마
│   ├── database.py            # 데이터베이스 연결 설정
│   ├── requirements.txt       # 의존성 패키지 목록
│   └── router/
│       ├── user_audio_router.py    # 🔥 오디오 분석 API (httpx 기반)
│       ├── script_router.py        # 스크립트 관련 API
│       ├── actor_router.py         # 배우 관련 API
│       └── token_router.py         # 토큰 관리 API
├── init-db/                   # 데이터베이스 초기화 스크립트
└── README.md                  # 이 파일
```

## 🛠️ 기술 스택

### 백엔드
- **FastAPI**: 현대적이고 빠른 웹 프레임워크
- **httpx**: 완전 비동기 HTTP 클라이언트
- **boto3**: AWS S3 연동
- **SQLAlchemy**: ORM
- **uvicorn**: ASGI 서버

### 인프라
- **AWS S3**: 오디오 파일 저장소
- **PostgreSQL**: 메인 데이터베이스
- **Railway**: 배포 플랫폼

## 🔧 설치 및 실행

### 1. 의존성 설치
```bash
cd back-end
pip install -r requirements.txt
```

### 2. 환경 변수 설정
```bash
# .env 파일 생성
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=your_aws_region
S3_BUCKET_NAME=your_s3_bucket_name
TARGET_SERVER_URL=http://43.201.26.49:8000/analyze-voice
WEBHOOK_URL=https://yousync-fastapi-production.up.railway.app/webhook/analysis-complete
DATABASE_URL=postgresql://username:password@localhost/dbname
```

### 3. 데이터베이스 초기화
```bash
python init_db.py
```

### 4. 서버 실행
```bash
# 개발 모드
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 모드
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📡 API 엔드포인트

### 오디오 분석 API (`/tokens`)

#### 1. 오디오 업로드 및 분석 요청
```http
POST /tokens/{token_id}/upload-audio
Content-Type: multipart/form-data

Parameters:
- token_id (path): 토큰 ID
- file (form-data): 오디오 파일

Response:
{
  "message": "업로드 완료, 백그라운드에서 처리됩니다.",
  "job_id": "uuid-string",
  "status": "processing"
}
```

#### 2. 분석 결과 조회
```http
GET /tokens/analysis-result/{job_id}

Response:
{
  "status": "completed|processing|failed",
  "token_id": "string",
  "progress": 100,
  "result": {...},
  "message": "분석 완료"
}
```

#### 3. 실시간 진행 상황 (SSE)
```http
GET /tokens/analysis-progress/{job_id}
Accept: text/event-stream

Response Stream:
data: {"status": "processing", "progress": 40, "message": "S3 업로드 중..."}
data: {"status": "processing", "progress": 70, "message": "분석 서버 요청 중..."}
data: {"status": "completed", "progress": 100, "result": {...}}
```

#### 4. 웹훅 엔드포인트
```http
POST /tokens/webhook/analysis-complete?job_id=uuid-string

Request Body:
{
  "status": "success",
  "result": {...}
}
```

## 🏗️ 아키텍처

### 비동기 처리 흐름

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant S3
    participant AnalysisServer
    participant Webhook

    Client->>FastAPI: POST /upload-audio
    FastAPI->>Client: job_id (즉시 응답)
    
    Note over FastAPI: BackgroundTasks 시작
    FastAPI->>S3: 비동기 파일 업로드 (ThreadPoolExecutor)
    FastAPI->>AnalysisServer: httpx 비동기 요청
    
    Client->>FastAPI: GET /analysis-progress/{job_id} (SSE)
    FastAPI-->>Client: 실시간 진행 상황 스트림
    
    AnalysisServer->>Webhook: 분석 완료 알림
    FastAPI->>Client: 분석 완료 (SSE)
```

### 핵심 컴포넌트

1. **httpx AsyncClient**: 외부 API 호출을 위한 완전 비동기 HTTP 클라이언트
2. **ThreadPoolExecutor**: S3 업로드와 같은 I/O 작업의 비동기 처리
3. **BackgroundTasks**: FastAPI의 백그라운드 작업 처리
4. **Server-Sent Events**: 실시간 진행 상황 스트리밍
5. **메모리 저장소**: 작업 상태 추적 (프로덕션에서는 Redis/DB 권장)

## 🔄 이전 버전과의 차이점

### Before (Celery/Redis)
```python
# 복잡한 설정과 의존성
from celery import Celery
import redis

app = Celery('tasks', broker='redis://localhost:6379')

@app.task
def process_audio(file_path):
    # 동기식 처리
    pass
```

### After (httpx/FastAPI)
```python
# 간단하고 직관적
import httpx
from fastapi import BackgroundTasks

async def send_analysis_request_async(s3_url: str, job_id: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(TARGET_URL, data={...})
        # 완전 비동기 처리
```

## 📈 성능 개선

- **의존성 감소**: Celery, Redis, aiohttp 제거
- **메모리 효율성**: 불필요한 워커 프로세스 제거
- **응답성 향상**: 비동기 I/O로 더 빠른 응답
- **배포 단순화**: 단일 프로세스로 배포 복잡도 감소

## 🧪 테스트

### API 테스트
```bash
# 서버 실행 확인
curl http://localhost:8000/docs

# 오디오 업로드 테스트
curl -X POST "http://localhost:8000/tokens/test-token/upload-audio" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_audio.wav"

# 결과 조회
curl http://localhost:8000/tokens/analysis-result/{job_id}

# SSE 스트림 테스트
curl -N http://localhost:8000/tokens/analysis-progress/{job_id}
```

### 실행 예시
```bash
# 1. 서버 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 2. Swagger UI 접속
# http://localhost:8000/docs

# 3. 오디오 업로드 (응답 예시)
{
  "message": "업로드 완료, 백그라운드에서 처리됩니다.",
  "job_id": "73732cad-5149-44d4-a954-e9c4781635c3",
  "status": "processing"
}

# 4. 진행 상황 확인
{
  "status": "processing",
  "progress": 90,
  "message": "분석 중... 결과 대기",
  "s3_url": "s3://bucket/audio/uuid_filename.wav"
}
```

## 🚧 개발 예정

- [ ] 데이터베이스 기반 작업 상태 저장
- [ ] 인증/권한 시스템 강화
- [ ] 멀티파트 대용량 파일 업로드 지원
- [ ] 분석 결과 캐싱 시스템
- [ ] 모니터링 및 로깅 개선

## 📝 라이센스

MIT License

## 🤝 기여

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 연락처

프로젝트 관련 문의: [이메일 주소]

---

**⚡ 이제 Celery와 Redis 없이도 강력한 비동기 오디오 분석 서비스를 운영할 수 있습니다!**
