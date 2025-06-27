# 🎬 영화/스크립트 관리 API 서버

FastAPI + PostgreSQL을 사용한 영화 및 스크립트 관리 시스템입니다. 음성 분석 기능을 포함한 완전한 REST API를 제공합니다.

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

이 프로젝트는 영화와 스크립트(대사) 데이터를 효율적으로 관리할 수 있는 REST API 서버입니다. 
특히 음성 분석 기능을 통해 배우의 음성 피치와 배경음을 분석하여 저장할 수 있는 특화된 기능을 제공합니다.

### 주요 특징
- 🎭 **영화 정보 관리**: 배우, 카테고리, 재생시간 등 기본 정보
- 📝 **스크립트 관리**: 대사 원문/번역, 시간 구간, 음성 분석 데이터
- 🎵 **음성 분석**: 배우 음성과 배경음의 피치 값 시계열 데이터 저장
- 🔍 **고급 검색**: 배우별, 카테고리별 영화 검색 기능
- 📖 **자동 문서화**: Swagger UI와 ReDoc을 통한 API 문서 자동 생성

## ✨ 주요 기능

### 🎬 영화 관리
- **CRUD 작업**: 영화 생성, 조회, 수정, 삭제
- **카테고리별 검색**: 로맨스, 액션, 드라마 등 장르별 영화 조회
- **배우별 검색**: 특정 배우가 출연한 영화 목록 조회
- **북마크 기능**: 관심 영화 북마크 설정
- **페이지네이션**: 대용량 데이터 효율적 처리

### 📝 스크립트 관리
- **CRUD 작업**: 스크립트 생성, 조회, 수정, 삭제
- **시간 구간 관리**: 대사의 정확한 시작/끝 시간 저장
- **다국어 지원**: 원문과 번역문 동시 관리
- **음성 분석 데이터**: 배우 음성과 배경음의 피치 값 저장
- **YouTube 연동**: 영상 URL 링크 관리

### 🔊 음성 분석 기능
- **배우 음성 피치**: JSON 배열 형태의 시계열 피치 데이터
- **배경음 피치**: 배경음악/효과음의 피치 분석 데이터
- **구간별 분석**: 대사 시작/끝 시간에 따른 정밀 분석

## 🛠️ 기술 스택

### Backend
- **FastAPI**: 고성능 Python 웹 프레임워크
- **SQLAlchemy**: Python ORM (Object Relational Mapping)
- **Pydantic**: 데이터 검증 및 직렬화
- **Uvicorn**: ASGI 서버

### Database
- **PostgreSQL**: 관계형 데이터베이스 (프로덕션)
- **SQLite**: 로컬 개발용 (옵션)

### Development Tools
- **python-dotenv**: 환경변수 관리
- **python-multipart**: 파일 업로드 지원

## 📁 프로젝트 구조

```
fast-api/
├── back-end/
│   ├── main.py                 # FastAPI 애플리케이션 진입점
│   ├── database.py             # 데이터베이스 연결 설정
│   ├── models.py               # SQLAlchemy ORM 모델
│   ├── schemas.py              # Pydantic 스키마 정의
│   ├── requirements.txt        # Python 의존성 패키지
│   ├── .env                    # 환경변수 설정 파일
│   ├── add_dummy_data.py       # 테스트 데이터 생성 스크립트
│   └── router/
│       ├── __init__.py
│       ├── script_router.py    # 스크립트 관련 API 엔드포인트
│       └── movie_router.py     # 영화 관련 API 엔드포인트
├── docker-compose.yml          # Docker 컨테이너 설정
└── README.md                   # 프로젝트 문서
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
```

### 6. 데이터베이스 초기화
```bash
# 애플리케이션 실행 시 자동으로 테이블이 생성됩니다
# 또는 테스트 데이터 추가
python add_dummy_data.py
```

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

#### 🎬 영화 API (`/movies`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/movies/` | 모든 영화 목록 조회 |
| POST | `/movies/` | 새 영화 생성 |
| GET | `/movies/{movie_id}` | 특정 영화 조회 |
| PUT | `/movies/{movie_id}` | 영화 정보 수정 |
| DELETE | `/movies/{movie_id}` | 영화 삭제 |
| GET | `/movies/category/{category}` | 카테고리별 영화 조회 |
| GET | `/movies/actor/{actor}` | 배우별 영화 조회 |

#### 📝 스크립트 API (`/scripts`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/scripts/` | 모든 스크립트 목록 조회 |
| POST | `/scripts/` | 새 스크립트 생성 |
| GET | `/scripts/{script_id}` | 특정 스크립트 조회 |
| PUT | `/scripts/{script_id}` | 스크립트 정보 수정 |
| DELETE | `/scripts/{script_id}` | 스크립트 삭제 |

## 🗄️ 데이터베이스 구조

### Movies 테이블
```sql
CREATE TABLE movies (
    id SERIAL PRIMARY KEY,
    actor VARCHAR,           -- 주연배우
    total_time INTEGER,      -- 재생시간(분)
    category VARCHAR,        -- 카테고리
    url VARCHAR,            -- YouTube URL
    bookmark BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

### Scripts 테이블
```sql
CREATE TABLE scripts (
    id SERIAL PRIMARY KEY,
    actor VARCHAR,                    -- 배우 이름
    start_time FLOAT,                -- 대사 시작 시간(초)
    end_time FLOAT,                  -- 대사 끝 시간(초)
    script TEXT,                     -- 대사 원문
    translation TEXT,                -- 대사 번역
    url VARCHAR,                     -- YouTube URL
    actor_pitch_values JSON,         -- 배우 음성 피치 배열
    background_pitch_values JSON,    -- 배경음 피치 배열
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

## 💡 사용 예시

### 영화 생성
```bash
curl -X POST "http://localhost:8000/movies/" \
  -H "Content-Type: application/json" \
  -d '{
    "actor": "김민수",
    "total_time": 120,
    "category": "로맨스",
    "url": "https://youtube.com/watch?v=example",
    "bookmark": false
  }'
```

### 스크립트 생성 (음성 분석 데이터 포함)
```bash
curl -X POST "http://localhost:8000/scripts/" \
  -H "Content-Type: application/json" \
  -d '{
    "actor": "김민수",
    "start_time": 15.5,
    "end_time": 18.2,
    "script": "안녕하세요, 만나서 반가워요!",
    "translation": "Hello, nice to meet you!",
    "url": "https://youtube.com/watch?v=example",
    "actor_pitch_values": [120, 125, 118, 130, 115],
    "background_pitch_values": [80, 82, 78, 85, 79]
  }'
```

### 카테고리별 영화 검색
```bash
curl "http://localhost:8000/movies/category/로맨스?skip=0&limit=10"
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

### 데이터베이스 스키마 확인
SQLAlchemy가 자동으로 테이블을 생성하므로, 모델 변경 시 데이터베이스를 초기화하거나 마이그레이션 도구를 사용하세요.

### 환경 분리
- **개발**: SQLite 사용 (간단한 설정)
- **프로덕션**: PostgreSQL 사용 (성능 및 확장성)

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
