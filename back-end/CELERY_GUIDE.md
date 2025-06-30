# Celery 설정 및 실행 가이드

## 📦 설치

```bash
# 새로운 의존성 설치
pip install celery redis

# 또는 requirements.txt에서 일괄 설치
pip install -r requirements.txt
```

## 🚀 Redis 설치 및 실행

### macOS (Homebrew) - 권장
```bash
# Redis 설치
brew install redis

# Redis 서비스 시작 (백그라운드)
brew services start redis

# Redis 서비스 상태 확인
brew services list | grep redis

# Redis 연결 테스트
redis-cli ping
# 응답: PONG
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 연결 테스트
redis-cli ping
```

### Windows
```bash
# Windows Subsystem for Linux (WSL) 사용 권장
# 또는 Redis for Windows 다운로드
# https://github.com/microsoftarchive/redis/releases
```

## 🔧 환경변수 설정

`.env` 파일에 추가:
```env
# Redis 설정
REDIS_URL=redis://localhost:6379/0

# 프로덕션에서는 Redis Cloud 등 사용
# REDIS_URL=redis://username:password@host:port/db
```

## 🏃‍♂️ 실행 방법

### 1. Redis 서버 확인
```bash
redis-cli ping
# 응답: PONG
```

### 2. Celery 워커 시작 (별도 터미널)
```bash
cd back-end
celery -A celery_app worker --loglevel=info --queue=audio_queue
```

### 3. FastAPI 서버 시작
```bash
cd back-end
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Celery 모니터링 (선택사항)
```bash
# Flower 설치
pip install flower

# 모니터링 대시보드 실행
celery -A celery_app flower

# 브라우저에서 http://localhost:5555 접속
```

## 📊 성능 개선 효과

### 기존 방식
1. 파일 업로드 → S3 업로드 → 분석 요청 → 응답 대기
2. **총 시간: 30초~2분** (모든 작업을 동기적으로 처리)

### Celery 적용 후
1. 파일 읽기 → 즉시 응답 반환 ⚡
2. 백그라운드에서 S3 업로드 + 분석 요청
3. **응답 시간: 1~3초** (사용자는 즉시 결과 받음)

## 🔍 API 사용법

### 1. 오디오 업로드
```bash
curl -X POST "http://localhost:8000/tokens/test123/upload-audio" \
  -F "file=@audio.wav"

# 응답 (즉시 반환)
{
  "message": "업로드 완료, 분석이 백그라운드에서 진행됩니다.",
  "job_id": "abc123",
  "task_id": "def456",
  "status": "queued"
}
```

### 2. 진행 상황 확인
```bash
curl "http://localhost:8000/tokens/analysis-result/abc123"

# 응답 예시
{
  "status": "processing",
  "progress": 40,
  "message": "S3 업로드 완료, 분석 서버 요청 중",
  "s3_url": "s3://bucket/audio/file.wav"
}
```

### 3. 실시간 진행 상황 (SSE)
```javascript
// 프론트엔드에서 실시간 업데이트
const eventSource = new EventSource('http://localhost:8000/tokens/analysis-progress/abc123');

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log(`진행률: ${data.progress}% - ${data.message}`);
  
  if (data.status === 'completed') {
    console.log('분석 완료!', data.result);
    eventSource.close();
  }
};
```

## 🛠️ 문제 해결

### Redis 연결 오류
```bash
# Redis 서버 상태 확인
redis-cli ping

# Redis 프로세스 확인
ps aux | grep redis

# Redis 재시작
brew services restart redis  # macOS
sudo systemctl restart redis-server  # Linux
```

### Celery 워커 오류
```bash
# 워커 로그 확인
celery -A celery_app worker --loglevel=debug

# 큐 상태 확인
celery -A celery_app inspect active
```

### 메모리 사용량 최적화
```bash
# 워커 프로세스 수 제한
celery -A celery_app worker --concurrency=2

# 메모리 제한 설정
celery -A celery_app worker --max-memory-per-child=300000  # 300MB
```
