# 🎬 영화/스크립트 관리 API

FastAPI + PostgreSQL을 사용한 영화 및 스크립트 관리 시스템입니다.
Docker를 사용하여 팀 전체가 동일한 개발 환경에서 작업할 수 있습니다.

## 🚀 빠른 시작 (Docker 사용)

### 🔧 개발 환경 선택

**방법 1: VS Code Dev Container 사용 (추천)**
1. VS Code에서 프로젝트 폴더 열기
2. "Reopen in Container" 알림 클릭 또는 `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"
3. 자동으로 모든 환경이 설정됩니다!

**방법 2: 로컬 개발 + Docker 서비스**
```bash
# 백그라운드에서 DB와 pgAdmin만 실행
docker-compose up -d
# VS Code에서 로컬 Python 환경으로 개발
```

### 사전 준비사항
- [Docker Desktop](https://www.docker.com/get-started) 설치 및 실행
- Git 설치

### 1단계: 프로젝트 클론
```bash
git clone <repository-url>
cd fast-api
```

### 2단계: 환경변수 설정
```bash
# 환경변수 예시 파일을 복사하여 실제 환경변수 파일 생성
cp .env.example .env
```

### 3단계: Docker 컨테이너 시작
```bash
# 모든 서비스 시작 (백그라운드)
docker-compose up -d

# 시작 상태 확인
docker-compose ps

# 로그 확인 (선택사항)
docker-compose logs -f
```

### 4단계: 접속 확인
- **API 서버**: http://localhost:8000
- **API 문서 (Swagger)**: http://localhost:8000/docs
- **pgAdmin (DB 관리)**: http://localhost:5050
  - 이메일: admin@example.com
  - 비밀번호: admin123

## 🐳 Docker 서비스 구성

### 서비스 목록
- **api**: FastAPI 백엔드 서버 (포트 8000)
- **db**: PostgreSQL 데이터베이스 (포트 5432)
- **pgadmin**: PostgreSQL 관리 도구 (포트 5050)

### 유용한 Docker 명령어
```bash
# 서비스 시작
docker-compose up -d

# 서비스 중지
docker-compose down

# 서비스 재시작
docker-compose restart

# 로그 확인
docker-compose logs -f [서비스명]

# 컨테이너 상태 확인
docker-compose ps

# 데이터베이스 초기화 (주의: 모든 데이터 삭제됨)
docker-compose down -v
docker-compose up -d
```

## 🛠️ 개발 환경 설정

### 로컬 개발 (Docker 없이)
1. Python 가상환경 생성
```bash
cd back-end
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 의존성 설치
```bash
pip install -r requirements.txt
```

3. 환경변수 설정
```bash
# back-end/.env 파일 생성
cp .env.example .env
# 필요한 환경변수 수정
```

4. 서버 실행
```bash
uvicorn main:app --reload
```

## 📊 데이터베이스 관리

### pgAdmin 사용법
1. http://localhost:5050 접속
2. 로그인 (admin@example.com / admin123)
3. 서버 추가: 
   - Host: db
   - Port: 5432
   - Database: movie_script_db
   - Username: admin
   - Password: securepassword123

### 직접 데이터베이스 접속
```bash
docker-compose exec db psql -U admin -d movie_script_db
```

## 🔧 개발 팁

### 코드 변경사항 반영
- Docker 개발 환경에서는 코드 변경사항이 자동으로 반영됩니다 (볼륨 마운트)
- 새로운 패키지 설치 후에는 컨테이너 재빌드가 필요합니다:
```bash
docker-compose up -d --build
```

### 데이터베이스 스키마 변경
1. `back-end/models.py`에서 모델 수정
2. 컨테이너 재시작 (자동으로 테이블 생성/수정됨)

### 환경변수 관리
- `.env` 파일은 git에 커밋하지 마세요
- `.env.docker`는 템플릿 파일로 커밋해도 됩니다
- 프로덕션에서는 더 강력한 비밀번호를 사용하세요

## 🚀 프로덕션 배포

프로덕션 환경에서는 다음 사항들을 고려하세요:

1. **보안 강화**
   - 강력한 데이터베이스 비밀번호 사용
   - SECRET_KEY 변경
   - CORS 설정 제한

2. **성능 최적화**
   - 프로덕션용 Dockerfile 사용 (멀티 스테이지 빌드)
   - 환경변수 최적화
   - 로그 레벨 조정

3. **모니터링**
   - 헬스체크 엔드포인트 활용 (`/health`)
   - 로그 수집 설정

## 📝 API 문서

API 문서는 서버 실행 후 다음 URL에서 확인할 수 있습니다:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 기여하기

1. 브랜치 생성: `git checkout -b feature/새기능`
2. 변경사항 커밋: `git commit -am '새 기능 추가'`
3. 브랜치 푸시: `git push origin feature/새기능`
4. Pull Request 생성

## 📞 문제 해결

### 자주 발생하는 문제들

**1. 포트 충돌**
```bash
# 포트 사용 중인 프로세스 확인
lsof -i :8000
lsof -i :5432

# 포트 변경은 docker-compose.yml에서 수정
```

**2. 데이터베이스 연결 실패**
```bash
# 컨테이너 상태 확인
docker-compose ps

# 데이터베이스 로그 확인
docker-compose logs db
```

**3. 권한 문제**
```bash
# Docker 권한 확인
sudo usermod -aG docker $USER
# 재로그인 후 다시 시도
```

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 있습니다.
