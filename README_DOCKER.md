# 🐳 Docker를 사용한 영화/스크립트 관리 API 서버

이 프로젝트는 Docker와 Docker Compose를 사용하여 컨테이너화되었습니다.
모든 팀원이 동일한 환경에서 작업할 수 있습니다.

## 📋 사전 요구사항

- Docker Desktop 설치 (https://www.docker.com/products/docker-desktop)
- Docker Compose (Docker Desktop에 포함됨)

## 🚀 빠른 시작

### 1. 프로젝트 클론 및 이동
```bash
git clone <repository-url>
cd fast-api
```

### 2. Docker 컨테이너 빌드 및 실행
```bash
# 모든 서비스를 백그라운드에서 실행
docker-compose up -d

# 또는 로그를 보면서 실행
docker-compose up
```

### 3. 서비스 접근
- **FastAPI 서버**: http://localhost:8000
- **API 문서 (Swagger)**: http://localhost:8000/docs
- **pgAdmin (DB 관리)**: http://localhost:5050
  - 이메일: admin@example.com
  - 비밀번호: admin123

## 🛠️ 개발 명령어

### 컨테이너 관리
```bash
# 모든 서비스 시작
docker-compose up -d

# 특정 서비스만 시작
docker-compose up -d db
docker-compose up -d api

# 서비스 중지
docker-compose down

# 서비스 중지 + 볼륨 삭제 (데이터 완전 삭제)
docker-compose down -v

# 로그 확인
docker-compose logs api
docker-compose logs db

# 실시간 로그 모니터링
docker-compose logs -f api
```

### 컨테이너 내부 접근
```bash
# FastAPI 컨테이너 내부 접근
docker-compose exec api bash

# PostgreSQL 컨테이너 내부 접근
docker-compose exec db psql -U postgres -d movie_script_db
```

### 데이터베이스 관리
```bash
# 더미 데이터 추가 (컨테이너 내부에서)
docker-compose exec api python add_dummy_data.py

# 데이터베이스 백업
docker-compose exec db pg_dump -U postgres movie_script_db > backup.sql

# 데이터베이스 복원
docker-compose exec -T db psql -U postgres movie_script_db < backup.sql
```

## 🔧 개발 환경 설정

### 코드 수정 시
- `back-end` 폴더의 코드를 수정하면 자동으로 컨테이너에 반영됩니다 (볼륨 마운트)
- FastAPI는 `--reload` 옵션으로 실행되어 코드 변경 시 자동 재시작됩니다

### 새로운 패키지 추가 시
1. `requirements.txt`에 패키지 추가
2. 컨테이너 재빌드: `docker-compose up --build api`

### 환경변수 수정 시
1. `docker-compose.yml`의 environment 섹션 수정
2. 또는 `.env.docker` 파일 수정 후 컨테이너 재시작

## 📊 서비스 구성

### 🗄️ Database (PostgreSQL)
- **컨테이너명**: movie_script_db
- **포트**: 5432
- **사용자**: postgres
- **비밀번호**: password123
- **데이터베이스**: movie_script_db

### 🚀 API Server (FastAPI)
- **컨테이너명**: movie_script_api
- **포트**: 8000
- **자동 재로드**: 활성화
- **API 문서**: http://localhost:8000/docs

### 🔧 pgAdmin (DB 관리 도구)
- **컨테이너명**: movie_script_pgadmin
- **포트**: 5050
- **웹 접근**: http://localhost:5050

## 🆘 트러블슈팅

### 컨테이너가 시작되지 않을 때
```bash
# 로그 확인
docker-compose logs

# 강제 재빌드
docker-compose up --build --force-recreate
```

### 데이터베이스 연결 오류
```bash
# DB 컨테이너 상태 확인
docker-compose ps db

# DB 헬스체크 확인
docker-compose exec db pg_isready -U postgres
```

### 포트 충돌 오류
- 로컬에서 이미 사용 중인 포트가 있는지 확인
- `docker-compose.yml`에서 포트 번호 변경

## 🎯 프로덕션 배포

프로덕션 환경에서는:
1. 환경변수에서 비밀번호 강화
2. SSL/TLS 설정 추가
3. 로그 레벨 조정
4. 리소스 제한 설정

---

## 👥 팀원 온보딩

새로운 팀원이 합류할 때:
1. Docker Desktop 설치
2. 프로젝트 클론
3. `docker-compose up -d` 실행
4. http://localhost:8000/docs 접속하여 확인

끝! 🎉
