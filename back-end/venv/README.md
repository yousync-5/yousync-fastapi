# � YouSync - 개인 더빙 플랫폼 API 서버

FastAPI + PostgreSQL을 사용한 토큰 기반 음성 분석 및 더빙 시스템입니다. 사용자 맞춤형 음성 분석과 오디오 업로드 기능을 제공합니다.

## 📋 목차
- [프로젝트 개요](#-프로젝트-개요)
- [주요 기능](#-주요-기능)
- [기술 스택](#️-기술-스택)
- [프로젝트 구조](#-프로젝트-구조)
- [설치 및 실행](#-설치-및-실행)
- [API 문서](#-api-문서)
- [데이터베이스 구조](#️-데이터베이스-구조)
- [사용 예시](#-사용-예시)
- [배포 정보](#-배포-정보)

## 🎯 프로젝트 개요

이 프로젝트는 토큰 기반 음성 분석과 개인 더빙을 위한 REST API 서버입니다. 
영화 클립의 대사를 토큰 단위로 분석하고, 사용자가 자신의 음성을 업로드하여 개인 더빙 콘텐츠를 제작할 수 있는 플랫폼입니다.

### 주요 특징
- 🎭 **토큰 기반 관리**: 배우별 대사를 토큰 단위로 세분화하여 관리
- 📝 **스크립트 분석**: 대사의 정확한 시간 구간과 텍스트 데이터 저장
- 🎵 **음성 분석**: TextGrid, Pitch, 배경음성 등 다양한 음성 분석 데이터 지원
- � **사용자 오디오**: 개인 더빙 음성 업로드 및 관리 기능
- 🌐 **S3 연동**: AWS S3를 통한 안정적인 오디오 파일 저장 및 스트리밍

## ✨ 주요 기능

### � 토큰 기반 음성 관리
- **CRUD 작업**: 토큰 생성, 조회, 수정, 삭제
- **배우별 관리**: 특정 배우의 토큰 그룹화 및 관리
- **시간 구간 설정**: 대사의 정확한 시작/끝 시간 저장
- **음성 분석 데이터**: TextGrid, Pitch, 배경음성 URL 관리
- **YouTube 연동**: 원본 영상 URL 링크 관리

### � 스크립트 분석
- **문장 단위 분할**: 토큰 내 문장별 세분화 관리
- **시간 동기화**: 각 문장의 정확한 타이밍 정보
- **텍스트 매칭**: 음성과 텍스트의 정확한 동기화

### 🔊 사용자 오디오 업로드
- **개인 더빙**: 사용자가 직접 녹음한 음성 업로드
- **파일 검증**: 음성 파일 형식 및 품질 검증
- **S3 저장**: 안정적인 클라우드 스토리지를 통한 파일 관리
- **분석 연동**: 업로드된 음성의 자동 분석 트리거

## 🛠️ 기술 스택

### Backend
- **FastAPI**: 고성능 Python 웹 프레임워크
- **SQLAlchemy**: Python ORM (Object Relational Mapping)
- **Pydantic**: 데이터 검증 및 직렬화
- **Uvicorn**: ASGI 서버

### Database
- **PostgreSQL**: 관계형 데이터베이스 (프로덕션)
- **SQLite**: 로컬 개발용 (옵션)

### 클라우드 스토리지
- **AWS S3**: 음성 파일 저장 및 스트리밍
- **boto3**: AWS SDK for Python

### 파일 처리
- **python-multipart**: 파일 업로드 지원
- **yt-dlp**: 유튜브 영상 처리

### Development Tools
- **python-dotenv**: 환경변수 관리
- **requests**: HTTP 클라이언트

## 📁 프로젝트 구조

```
fast-api/
├── back-end/
│   ├── main.py                 # FastAPI 애플리케이션 진입점
│   ├── database.py             # 데이터베이스 연결 설정
│   ├── models.py               # SQLAlchemy ORM 모델 (토큰 기반 구조)
│   ├── schemas.py              # Pydantic 스키마 정의
│   ├── requirements.txt        # Python 의존성 패키지
│   ├── .env                    # 환경변수 설정 파일
│   ├── init_db.py             # 데이터베이스 초기화 스크립트
│   ├── add_dummy_data.py       # 테스트 데이터 생성 스크립트
│   ├── db.vuerd.json          # ERD 설계 파일
│   ├── router/                # API 라우터 모듈
│   │   ├── __init__.py
│   │   ├── script_router.py    # 스크립트 관련 API
│   │   ├── token_router.py     # 토큰 관련 API
│   │   ├── actor_router.py     # 배우 관련 API
│   │   ├── user_audio_router.py # 사용자 오디오 업로드 API
│   │   └── analysis_router_backup.py # 백업 파일
│   ├── media/                 # 정적 파일 저장소
│   │   └── audio/             # 로컬 오디오 파일
│   ├── storage/               # 파일 저장소
│   │   ├── actor_encodings/   # 배우 얼굴 인코딩 파일
│   │   ├── actor_images/      # 배우 이미지
│   │   ├── scene_frames/      # 영상 프레임 이미지
│   │   ├── audio/             # 오디오 파일
│   │   └── subtitles/         # 자막 파일
│   └── venv/                  # Python 가상환경
├── init-db/                   # 데이터베이스 초기화 관련 파일
├── request_test.py            # API 테스트 스크립트
├── package-lock.json          # Node.js 의존성 (프론트엔드 연동용)
└── README.md                  # 프로젝트 문서
```

## 🚀 설치 및 실행

### 1. 사전 요구사항
- Python 3.11+
- PostgreSQL (또는 Docker)
- Git

### 2. 프로젝트 클론
```bash
git clone <repository-url>
cd fast-api/back-end
```

### 3. 가상환경 설정 (권장)
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 4. 의존성 설치
```bash
pip install -r requirements.txt
```

### 5. 환경변수 설정
`.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# PostgreSQL 설정 (프로덕션)
DATABASE_URL=postgresql+psycopg2://username:password@host:port/database

# 또는 SQLite 설정 (로컬 개발)
DATABASE_URL=sqlite:///./test.db

# AWS S3 설정 (오디오 파일 저장용)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=your_bucket_name
```

**AWS S3 설정 방법:**
- **AWS 계정**: AWS 콘솔에서 IAM 사용자 생성 및 S3 권한 부여
- **S3 버킷**: 오디오 파일 저장용 버킷 생성
- **참고**: AWS 설정 없이는 로컬 파일 시스템을 사용합니다.

### 6. 데이터베이스 초기화
```bash
# 수동으로 데이터베이스 초기화 (선택사항)
python init_db.py

# 테스트 데이터 추가 (선택사항)
python add_dummy_data.py
```

**참고**: 애플리케이션 실행 시 자동으로 테이블이 생성됩니다.

### 7. 서버 실행

#### 개발 모드 (자동 리로드)
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 프로덕션 모드
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 8. 서버 접속 확인
- 메인 페이지: http://localhost:8000
- API 문서 (Swagger): http://localhost:8000/docs
- API 문서 (ReDoc): http://localhost:8000/redoc

## 📖 API 문서

### 자동 생성 문서
FastAPI는 자동으로 대화형 API 문서를 생성합니다:

- **Swagger UI**: http://localhost:8000/docs
  - 직접 API 테스트 가능
  - 요청/응답 예시 제공
  - 인증 기능 지원

- **ReDoc**: http://localhost:8000/redoc
  - 깔끔한 문서 형태
  - 인쇄 친화적 레이아웃

### 주요 엔드포인트

#### � 토큰 API (`/tokens`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/tokens/` | 모든 토큰 목록 조회 |
| POST | `/tokens/` | 새 토큰 생성 |
| GET | `/tokens/{token_id}` | 특정 토큰 조회 |
| PUT | `/tokens/{token_id}` | 토큰 정보 수정 |
| DELETE | `/tokens/{token_id}` | 토큰 삭제 |

#### 📝 스크립트 API (`/scripts`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/scripts/` | 모든 스크립트 목록 조회 |
| POST | `/scripts/` | 새 스크립트 생성 |
| GET | `/scripts/{script_id}` | 특정 스크립트 조회 |
| PUT | `/scripts/{script_id}` | 스크립트 정보 수정 |
| DELETE | `/scripts/{script_id}` | 스크립트 삭제 |
| GET | `/scripts/token/{token_id}` | 토큰별 스크립트 조회 |

#### 🎭 배우 API (`/actors`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/actors/` | 모든 배우 목록 조회 |
| POST | `/actors/` | 새 배우 생성 |
| GET | `/actors/{actor_id}` | 특정 배우 조회 |
| PUT | `/actors/{actor_id}` | 배우 정보 수정 |
| DELETE | `/actors/{actor_id}` | 배우 삭제 |

#### 🔊 사용자 오디오 API (`/tokens/{token_id}/upload-audio`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/tokens/{token_id}/upload-audio` | 사용자 오디오 파일 업로드 |
| POST | `/webhook/analysis-complete` | 분석 완료 웹훅 |
| GET | `/analysis-result/{job_id}` | 분석 결과 조회 |

## 🗄️ 데이터베이스 구조

### � Tokens 테이블
```sql
CREATE TABLE tokens (
    id SERIAL PRIMARY KEY,
    token_name VARCHAR NOT NULL,             -- 토큰 이름
    actor_name VARCHAR NOT NULL,             -- 배우 이름
    start_time FLOAT NOT NULL,               -- 토큰 시작 시간(초)
    end_time FLOAT NOT NULL,                 -- 토큰 끝 시간(초)
    s3_textgrid_url TEXT,                    -- TextGrid 파일 S3 URL
    s3_pitch_url TEXT,                       -- Pitch 분석 파일 S3 URL
    s3_bgvoice_url TEXT,                     -- 배경음성 파일 S3 URL
    youtube_url TEXT                         -- YouTube URL
);
```

### 🎭 Actors 테이블
```sql
CREATE TABLE actors (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL     -- 배우 이름 (고유값)
);
```

### 📝 Scripts 테이블
```sql
CREATE TABLE scripts (
    id SERIAL PRIMARY KEY,
    token_id INTEGER NOT NULL,               -- 토큰 ID (외래키)
    start_time FLOAT NOT NULL,               -- 문장 시작 시간(초)
    end_time FLOAT NOT NULL,                 -- 문장 끝 시간(초)
    script TEXT NOT NULL,                    -- 문장 텍스트
    FOREIGN KEY (token_id) REFERENCES tokens(id)
);
```

### 🔗 MovieActors 테이블 (관계 테이블) - 레거시
```sql
CREATE TABLE movie_actors (
    movie_id INTEGER,                        -- 영화 ID (사용 안 함)
    actor_id INTEGER,                        -- 배우 ID (사용 안 함)
    PRIMARY KEY (movie_id, actor_id)
);
```
*현재 토큰 시스템에서는 사용하지 않는 레거시 테이블입니다.*

### 👥 Users 테이블
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE,         -- 사용자명
    email VARCHAR UNIQUE,            -- 이메일
    hashed_password VARCHAR          -- 해시된 비밀번호
);
```

### 🔄 주요 관계
- **Token ↔ Script**: 일대다 (한 토큰에 여러 문장)
- **Actor**: 독립적 관리 (배우 정보 저장)
- **Token.actor_name**: 배우 이름 직접 저장 (비정규화)

## 💡 사용 예시

### 토큰 생성
```bash
curl -X POST "http://localhost:8000/tokens/" \
  -H "Content-Type: application/json" \
  -d '{
    "token_name": "기생충_씬1_토큰1",
    "actor_name": "송강호",
    "start_time": 15.5,
    "end_time": 25.2,
    "s3_textgrid_url": "https://s3.amazonaws.com/bucket/token1.TextGrid",
    "s3_pitch_url": "https://s3.amazonaws.com/bucket/token1_pitch.json",
    "s3_bgvoice_url": "https://s3.amazonaws.com/bucket/token1_bg.wav",
    "youtube_url": "https://youtube.com/watch?v=example"
  }'
```

### 배우 생성
```bash
curl -X POST "http://localhost:8000/actors/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "송강호"
  }'
```

### 스크립트 생성
```bash
curl -X POST "http://localhost:8000/scripts/" \
  -H "Content-Type: application/json" \
  -d '{
    "token_id": 1,
    "start_time": 15.5,
    "end_time": 18.2,
    "script": "반지하에서 살고 있습니다"
  }'
```

### 사용자 오디오 업로드
```bash
curl -X POST "http://localhost:8000/tokens/1/upload-audio" \
  -F "file=@user_recording.wav" \
  -F "script_id=1" \
  -F "user_id=user123"
```

### 토큰별 스크립트 조회
```bash
curl "http://localhost:8000/scripts/token/1"
```

### 특정 배우 조회
```bash
curl "http://localhost:8000/actors/1"
```

## 🌐 배포 정보

### 현재 배포 환경
- **프로덕션 서버**: Railway
- **API 문서**: https://yousync-fastapi-production.up.railway.app/docs
- **데이터베이스**: PostgreSQL (Railway)

### Docker 배포
프로젝트 루트의 `docker-compose.yml`을 사용하여 컨테이너 기반 배포 가능:

```bash
docker-compose up -d
```

## 🔧 개발 팁

### 테스트 데이터 추가
```bash
python add_dummy_data.py
```

### 오디오 파일 처리

#### 1. 지원 파일 형식
- **업로드**: WAV, MP3, M4A, FLAC
- **처리**: 자동 형식 변환 및 검증
- **저장**: S3 버킷에 안전한 저장

#### 2. 파일 크기 제한
- **최대 크기**: 50MB
- **최적 품질**: 16kHz, 16-bit, Mono
- **자동 압축**: 업로드 시 자동 최적화

#### 3. S3 연동 개발 팁
```bash
# AWS CLI 설치 및 설정
pip install awscli
aws configure

# 버킷 생성 예시
aws s3 mb s3://your-bucket-name
aws s3api put-bucket-cors --bucket your-bucket-name --cors-configuration file://cors.json
```

### 로컬 개발 환경

#### 1. SQLite 사용 (간단한 설정)
```env
DATABASE_URL=sqlite:///./test.db
```

#### 2. PostgreSQL 사용 (프로덕션 환경과 동일)
```bash
# Docker로 PostgreSQL 실행
docker run -d \
  --name postgres-dev \
  -e POSTGRES_USER=dev \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=yousync \
  -p 5432:5432 \
  postgres:13
```

### API 테스트

#### 1. 내장 문서 활용
- **Swagger UI**: http://localhost:8000/docs
- **직접 테스트**: 웹 브라우저에서 API 호출 테스트

#### 2. 파일 업로드 테스트
```bash
# 오디오 파일 업로드 테스트
curl -X POST "http://localhost:8000/tokens/1/upload-audio" \
  -F "file=@test_audio.wav" \
  -F "script_id=1" \
  -F "user_id=test_user"
```

## 🚀 최신 업데이트 (2025.06.30)

### ✅ 완료된 작업 항목

#### 🎤 토큰 기반 시스템 구조 변경
- **Token 모델**: 배우별 대사 구간을 토큰 단위로 관리
- **Script 모델**: 토큰 내 문장별 세분화 구조
- **음성 분석 데이터**: S3 기반 TextGrid, Pitch, 배경음성 파일 관리
- **시간 동기화**: 정확한 타이밍 정보로 음성-텍스트 매칭

#### 🔊 사용자 오디오 업로드 시스템
- **파일 업로드**: FastAPI의 multipart 지원으로 안정적인 파일 처리
- **S3 연동**: boto3를 통한 클라우드 스토리지 관리
- **형식 검증**: 지원 오디오 형식 자동 검증
- **분석 연동**: 업로드된 파일의 자동 분석 트리거

#### �️ 기술 스택 현대화
- **FastAPI**: 최신 비동기 웹 프레임워크
- **AWS S3**: 확장 가능한 오디오 파일 저장소
- **PostgreSQL**: 안정적인 관계형 데이터베이스
- **yt-dlp**: 최신 유튜브 처리 라이브러리

### 🎯 프로젝트의 현재 방향성

#### 핵심 가치
1. **개인화**: 사용자 맞춤형 더빙 콘텐츠 제작
2. **정밀성**: 토큰 단위의 세밀한 음성 분석
3. **확장성**: 클라우드 기반 인프라로 무제한 성장

#### 시스템 아키텍처
- **토큰 관리**: 배우별 대사 구간의 체계적 관리
- **음성 분석**: 다차원 음성 데이터 (TextGrid, Pitch, 배경음)
- **사용자 참여**: 개인 더빙 음성 업로드 및 분석
- **클라우드 연동**: S3 기반 안정적 파일 스토리지

#### 현재 API 상태
- **Token API**: ✅ 토큰 CRUD 및 음성 분석 데이터 관리
- **Script API**: ✅ 문장 단위 세분화 및 타이밍 관리
- **Actor API**: ✅ 배우 정보 관리
- **User Audio API**: ✅ 사용자 오디오 업로드 및 처리

### 🏗️ 기술적 성과

#### 데이터 구조 최적화
- 토큰-스크립트 관계로 계층적 데이터 관리
- S3 URL 기반 파일 참조로 확장성 확보
- 비정규화된 배우 이름으로 조회 성능 향상

#### 파일 처리 시스템
- 다중 오디오 형식 지원 (WAV, MP3, M4A, FLAC)
- 자동 파일 검증 및 형식 변환
- 클라우드 기반 확장 가능한 저장소

#### API 설계 철학
- RESTful 구조로 일관된 인터페이스
- FastAPI의 자동 문서화로 개발 효율성
- 비동기 처리로 고성능 구현

### 📊 실제 사용 시나리오

```bash
# 1. 토큰 생성 (음성 분석 데이터 포함)
POST /tokens/ {
  "token_name": "기생충_씬1",
  "actor_name": "송강호",
  "s3_textgrid_url": "s3://bucket/analysis.TextGrid",
  "s3_pitch_url": "s3://bucket/pitch.json",
  "s3_bgvoice_url": "s3://bucket/background.wav"
}

# 2. 스크립트 세분화
POST /scripts/ {
  "token_id": 1,
  "script": "반지하에서 살고 있습니다"
}

# 3. 사용자 더빙 업로드
POST /tokens/1/upload-audio (multipart/form-data)
- file: user_recording.wav
- script_id: 1
- user_id: user123

# 4. 결과 확인
GET /scripts/token/1  # 토큰별 스크립트 조회
```

프로젝트가 **개인 더빙 플랫폼의 핵심 API**로 성공적으로 진화했습니다! 🎉

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 등록해 주세요.

---

**Happy Coding! 🚀**
