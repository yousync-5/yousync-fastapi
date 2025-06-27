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

### 🎥 YouTube 영상 분석 (신규 추가)
- **메타데이터 추출**: 유튜브 영상 제목, 설명, 태그, 조회수 등 정보 추출
- **배우 정보 조회**: TMDb API를 통한 영화 출연진 정보 자동 조회
- **배우 이미지 크롤링**: 구글 이미지 검색을 통한 배우 사진 자동 수집
- **얼굴 인식 및 매칭**: OpenCV와 face_recognition을 통한 영상 내 배우 얼굴 매칭
- **음성 전사**: OpenAI Whisper를 통한 영상 음성의 텍스트 변환
- **자동화된 분석 파이프라인**: 유튜브 링크 하나로 전체 분석 과정 자동화

## 🛠️ 기술 스택

### Backend
- **FastAPI**: 고성능 Python 웹 프레임워크
- **SQLAlchemy**: Python ORM (Object Relational Mapping)
- **Pydantic**: 데이터 검증 및 직렬화
- **Uvicorn**: ASGI 서버

### Database
- **PostgreSQL**: 관계형 데이터베이스 (프로덕션)
- **SQLite**: 로컬 개발용 (옵션)

### 영상/음성 분석
- **OpenCV**: 컴퓨터 비전 및 영상 처리
- **face_recognition**: 얼굴 인식 라이브러리
- **OpenAI Whisper**: 음성 인식 및 전사
- **yt-dlp**: 유튜브 영상 다운로드
- **FFmpeg**: 멀티미디어 처리

### 외부 API 연동
- **TMDb API**: 영화 정보 및 출연진 데이터
- **Google Custom Search API**: 배우 이미지 크롤링

### Development Tools
- **python-dotenv**: 환경변수 관리
- **python-multipart**: 파일 업로드 지원
- **Pillow**: 이미지 처리
- **requests**: HTTP 클라이언트

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
│   ├── router/
│   │   ├── __init__.py
│   │   ├── script_router.py    # 스크립트 관련 API 엔드포인트
│   │   ├── movie_router.py     # 영화 관련 API 엔드포인트
│   │   └── analysis_router.py  # 영상 분석 관련 API 엔드포인트 (신규)
│   ├── services/               # 비즈니스 로직 서비스 (신규)
│   │   ├── __init__.py
│   │   ├── youtube_service.py  # 유튜브 메타데이터 추출
│   │   ├── actor_service.py    # 배우 정보 조회 (TMDb API)
│   │   ├── crawl_service.py    # 배우 이미지 크롤링
│   │   ├── face_service.py     # 얼굴 인식 및 매칭
│   │   └── whisper_service.py  # 음성 전사
│   └── storage/                # 파일 저장소 (신규)
│       ├── actor_encodings/    # 배우 얼굴 인코딩 파일
│       ├── scene_frames/       # 추출된 영상 프레임
│       └── audio/              # 추출된 오디오 파일
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

# 영상 분석 API 키들 (신규 추가)
TMDB_API_KEY=your_tmdb_api_key_here
GOOGLE_API_KEY=your_google_custom_search_api_key_here
GOOGLE_CX=your_google_custom_search_engine_id_here
```

**API 키 발급 방법:**
- **TMDb API**: https://www.themoviedb.org/settings/api 에서 발급
- **Google Custom Search API**: Google Cloud Console에서 Custom Search API 활성화
- **Google Custom Search Engine**: https://cse.google.com/ 에서 검색 엔진 생성

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
| GET | `/movies/actor/{actor_name}` | 배우별 영화 조회 |

#### 🎭 배우 API (`/actors`) - 신규 추가
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/actors/` | 모든 배우 목록 조회 |
| POST | `/actors/` | 새 배우 생성 |
| GET | `/actors/{actor_id}` | 특정 배우 조회 |
| PUT | `/actors/{actor_id}` | 배우 정보 수정 |
| DELETE | `/actors/{actor_id}` | 배우 삭제 |
| GET | `/actors/search/{name}` | 배우 이름으로 검색 |
| GET | `/actors/{actor_id}/movies` | 배우 출연 영화 목록 |

#### 📝 스크립트 API (`/scripts`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/scripts/` | 모든 스크립트 목록 조회 |
| POST | `/scripts/` | 새 스크립트 생성 |
| GET | `/scripts/{script_id}` | 특정 스크립트 조회 |
| PUT | `/scripts/{script_id}` | 스크립트 정보 수정 |
| DELETE | `/scripts/{script_id}` | 스크립트 삭제 |
| GET | `/scripts/movie/{movie_id}` | 영화별 스크립트 조회 |
| GET | `/scripts/actor/{actor_id}` | 배우별 스크립트 조회 |

#### 🎥 영상 분석 API (`/analysis`) - 신규 추가
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/analysis/youtube/metadata` | 유튜브 메타데이터 추출 |
| POST | `/analysis/movie/actors` | 영화 출연진 정보 조회 |
| POST | `/analysis/full-analysis` | 전체 분석 파이프라인 시작 |
| POST | `/analysis/actors/crawl` | 배우 이미지 크롤링 |
| POST | `/analysis/face/match` | 영상 내 얼굴 매칭 |
| POST | `/analysis/audio/transcribe` | 음성 전사 |
| GET | `/analysis/health` | 분석 서비스 상태 확인 |

## 🗄️ 데이터베이스 구조

### 🎬 Movies 테이블
```sql
CREATE TABLE movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,          -- 영화 제목
    director VARCHAR,                -- 감독 이름
    release_year INTEGER,            -- 개봉 연도
    category VARCHAR,                -- 카테고리/장르
    youtube_url VARCHAR UNIQUE NOT NULL, -- YouTube URL
    total_time INTEGER,              -- 재생시간(분)
    bookmark BOOLEAN DEFAULT FALSE
);
```

### 🎭 Actors 테이블 (신규 추가)
```sql
CREATE TABLE actors (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,    -- 배우 이름 (고유값)
    tmdb_id INTEGER UNIQUE,          -- TMDb API ID
);
```

### 📝 Scripts 테이블 (구조 변경)
```sql
CREATE TABLE scripts (
    id SERIAL PRIMARY KEY,
    movie_id INTEGER NOT NULL,               -- 영화 ID (외래키)
    actor_id INTEGER NOT NULL,               -- 배우 ID (외래키)
    start_time FLOAT NOT NULL,               -- 대사 시작 시간(초)
    end_time FLOAT NOT NULL,                 -- 대사 끝 시간(초)
    script TEXT NOT NULL,                    -- 대사 원문
    translation TEXT,                        -- 대사 번역
    url VARCHAR,                             -- YouTube URL
    actor_pitch_values JSON,                 -- 배우 음성 피치 배열
    background_audio_url VARCHAR,            -- S3 배경음 파일 URL
    FOREIGN KEY (movie_id) REFERENCES movies(id),
    FOREIGN KEY (actor_id) REFERENCES actors(id)
);
```

### 🔗 MovieActors 테이블 (관계 테이블)
```sql
CREATE TABLE movie_actors (
    movie_id INTEGER,                        -- 영화 ID
    actor_id INTEGER,                        -- 배우 ID
    character_name VARCHAR,                  -- 극중 역할명
    PRIMARY KEY (movie_id, actor_id),
    FOREIGN KEY (movie_id) REFERENCES movies(id),
    FOREIGN KEY (actor_id) REFERENCES actors(id)
);
```

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
- **Movie ↔ Script**: 일대다 (한 영화에 여러 스크립트)
- **Actor ↔ Script**: 일대다 (한 배우가 여러 대사)
- **Movie ↔ Actor**: 다대다 (MovieActor 테이블을 통해 연결)

## 💡 사용 예시

### 영화 생성
```bash
curl -X POST "http://localhost:8000/movies/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "기생충",
    "director": "봉준호",
    "release_year": 2019,
    "category": "드라마",
    "youtube_url": "https://youtube.com/watch?v=example",
    "total_time": 132,
    "bookmark": false
  }'
```

### 배우 생성 (신규 추가)
```bash
curl -X POST "http://localhost:8000/actors/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "송강호",
    "tmdb_id": 17825
  }'
```

### 스크립트 생성 (구조 변경)
```bash
curl -X POST "http://localhost:8000/scripts/" \
  -H "Content-Type: application/json" \
  -d '{
    "movie_id": 1,
    "actor_id": 1,
    "start_time": 15.5,
    "end_time": 18.2,
    "script": "반지하에서 살고 있습니다",
    "translation": "We live in a semi-basement",
    "url": "https://youtube.com/watch?v=example",
    "actor_pitch_values": [120, 125, 118, 130, 115],
    "background_audio_url": "https://s3.amazonaws.com/bucket/audio/background_1.mp3"
  }'
```

### 배우별 영화 검색 (개선됨)
```bash
curl "http://localhost:8000/movies/actor/송강호"
```

### 영화별 스크립트 조회 (신규)
```bash
curl "http://localhost:8000/scripts/movie/1"
```

### 카테고리별 영화 검색
```bash
curl "http://localhost:8000/movies/category/로맨스?skip=0&limit=10"
```

### 🎥 YouTube 영상 분석 API 사용 예시 (신규)

#### 1. 유튜브 메타데이터 추출
```bash
curl -X POST "http://localhost:8000/analysis/youtube/metadata" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=example"
  }'
```

#### 2. 영화 출연진 정보 조회
```bash
curl -X POST "http://localhost:8000/analysis/movie/actors" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=example",
    "movie_title": "기생충"
  }'
```

#### 3. 배우 이미지 크롤링
```bash
curl -X POST "http://localhost:8000/analysis/actors/crawl" \
  -H "Content-Type: application/json" \
  -d '{
    "actors": ["송강호", "최우식", "박소담"],
    "max_images_per_actor": 10
  }'
```

#### 4. 영상 내 얼굴 매칭
```bash
curl -X POST "http://localhost:8000/analysis/face/match" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=example",
    "actors": ["송강호", "최우식"],
    "frame_interval": 30
  }'
```

#### 5. 음성 전사
```bash
curl -X POST "http://localhost:8000/analysis/audio/transcribe" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=example",
    "language": "ko"
  }'
```

#### 6. 전체 분석 파이프라인 실행
```bash
curl -X POST "http://localhost:8000/analysis/full-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=example",
    "movie_title": "기생충"
  }'
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

### 영상 분석 기능 개발 팁

#### 1. 저장소 디렉토리 구조
- `storage/actor_encodings/`: 배우별 얼굴 인코딩 파일 (.pkl)
- `storage/scene_frames/`: 영상에서 추출된 프레임 이미지
- `storage/audio/`: 영상에서 추출된 오디오 파일

#### 2. FFmpeg 설치 필요
영상/음성 처리를 위해 FFmpeg가 시스템에 설치되어 있어야 합니다:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# https://ffmpeg.org/download.html 에서 다운로드
```

#### 3. OpenCV 및 face_recognition 설치 주의사항
```bash
# macOS (Apple Silicon)
pip install --upgrade pip
pip install cmake
pip install dlib
pip install face-recognition

# 문제 발생 시 conda 사용 권장
conda install -c conda-forge dlib
conda install -c conda-forge face_recognition
```

#### 4. 백그라운드 작업 모니터링
현재 구현에서는 FastAPI의 BackgroundTasks를 사용하고 있습니다. 
대용량 처리가 필요한 경우 Celery + Redis 조합을 고려해보세요.

### 데이터베이스 스키마 확인
SQLAlchemy가 자동으로 테이블을 생성하므로, 모델 변경 시 데이터베이스를 초기화하거나 마이그레이션 도구를 사용하세요.

### 환경 분리
- **개발**: SQLite 사용 (간단한 설정)
- **프로덕션**: PostgreSQL 사용 (성능 및 확장성)

## 🚀 최신 업데이트 (2024.06.27)

### 🗄️ 데이터베이스 구조 대폭 개선 ✅

#### 📊 새로운 ERD 설계
- **정규화된 테이블 구조**: 데이터 중복을 제거하고 관계형 DB 설계 원칙 적용
- **외래키 관계 설정**: 데이터 무결성 보장 및 효율적인 조인 쿼리 지원
- **확장 가능한 아키텍처**: 향후 기능 추가를 고려한 유연한 설계

#### 🔄 주요 변경사항
1. **Actor 테이블 신규 추가**
   - 배우 정보를 별도 테이블로 분리 (중복 제거)
   - TMDb API와 연동을 위한 `tmdb_id` 필드 추가

2. **Script 테이블 구조 개선**
   - `actor` 문자열 → `actor_id` 외래키로 변경
   - `movie_id` 외래키 추가로 영화와 명확한 관계 설정
   - `background_pitch_values` → `background_audio_url`로 변경 (S3 연동)

3. **Movie 테이블 현대화**
   - `actor` 필드 제거 (MovieActor 관계 테이블로 대체)
   - `title`, `director`, `release_year` 필드 추가
   - `url` → `youtube_url`로 명확화

4. **MovieActor 관계 테이블 추가**
   - 영화-배우 다대다 관계 지원
   - `character_name` 필드로 극중 역할명 저장

#### 🎯 개선된 기능
- **정확한 데이터 관계**: 한 영화에 여러 배우, 한 배우가 여러 영화 출연 지원
- **중복 데이터 제거**: 배우 이름 중복 저장 문제 해결
- **향상된 검색**: 배우별/영화별 스크립트 조회 API 추가
- **확장성 증대**: TMDb API 연동으로 풍부한 메타데이터 지원

#### 🔗 새로운 API 엔드포인트
- `GET/POST/PUT/DELETE /actors/` - 배우 CRUD
- `GET /actors/search/{name}` - 배우 이름 검색
- `GET /actors/{actor_id}/movies` - 배우 출연작 조회
- `GET /scripts/movie/{movie_id}` - 영화별 스크립트 조회
- `GET /scripts/actor/{actor_id}` - 배우별 스크립트 조회

### 통합형 영상 분석 파이프라인 구축 완료 ✅

다음 기능들이 성공적으로 통합되었습니다:

#### 🎥 YouTube 영상 분석 시스템
- **메타데이터 추출**: `youtube_service.py` - 영상 정보 자동 추출
- **배우 정보 조회**: `actor_service.py` - TMDb API를 통한 출연진 정보
- **이미지 크롤링**: `crawl_service.py` - 구글 검색 기반 배우 사진 수집
- **얼굴 인식**: `face_service.py` - OpenCV + face_recognition 기반 매칭
- **음성 전사**: `whisper_service.py` - OpenAI Whisper 기반 STT

#### 📁 새로운 프로젝트 구조
```
services/          # 비즈니스 로직 분리
├── youtube_service.py
├── actor_service.py  
├── crawl_service.py
├── face_service.py
└── whisper_service.py

storage/           # 파일 저장소
├── actor_encodings/
├── scene_frames/
└── audio/

router/
└── analysis_router.py  # 7개 신규 API 엔드포인트
```

#### 🔗 통합 API 엔드포인트
- `POST /analysis/youtube/metadata` - 유튜브 메타데이터 추출
- `POST /analysis/movie/actors` - 영화 출연진 조회
- `POST /analysis/actors/crawl` - 배우 이미지 크롤링
- `POST /analysis/face/match` - 영상 내 얼굴 매칭
- `POST /analysis/audio/transcribe` - 음성 전사
- `POST /analysis/full-analysis` - 전체 파이프라인 실행
- `GET /analysis/health` - 서비스 상태 확인

#### 🛠️ 기술적 개선사항
- **의존성 패키지 추가**: requirements.txt에 영상/음성/AI 관련 21개 패키지 추가
- **환경변수 설정**: TMDb API, Google Custom Search API 키 관리
- **백그라운드 처리**: FastAPI BackgroundTasks를 통한 비동기 작업
- **에러 핸들링**: 각 서비스별 세밀한 예외 처리 및 로깅

### 🎯 사용 시나리오
1. **유튜브 URL 입력** → 메타데이터 자동 추출
2. **영화 정보 매칭** → TMDb에서 출연진 정보 조회
3. **배우 사진 수집** → 구글 이미지 검색으로 얼굴 DB 구축
4. **영상 분석** → 프레임별 얼굴 인식 및 매칭
5. **음성 추출** → Whisper로 대사 텍스트 변환
6. **결과 저장** → 기존 DB 스키마에 분석 결과 통합

모든 기능이 성공적으로 통합되어 단일 FastAPI 서버에서 완전한 영상 분석 파이프라인을 제공합니다! 🎉

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
