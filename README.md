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

### 🎥 YouTube 영상 분석
- **메타데이터 추출**: 유튜브 영상 제목, 설명, 태그, 조회수 등 정보 추출
- **배우 이미지 크롤링**: 구글 이미지 검색을 통한 배우 사진 자동 수집
- **얼굴 인식 및 매칭**: OpenCV와 face_recognition을 통한 영상 내 배우 얼굴 매칭
- **음성 전사**: OpenAI Whisper를 통한 영상 음성의 텍스트 변환
- **독립적인 분석 파이프라인**: 외부 API 의존성 없이 완전한 영상 분석

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
- **Google Custom Search API**: 배우 이미지 크롤링 (선택사항)

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
│   ├── models.py               # SQLAlchemy ORM 모델 (정규화된 단일 파일)
│   ├── schemas.py              # Pydantic 스키마 정의
│   ├── requirements.txt        # Python 의존성 패키지
│   ├── .env                    # 환경변수 설정 파일
│   ├── .gitignore             # Git 무시 파일
│   ├── init_db.py             # 데이터베이스 초기화 스크립트
│   ├── add_dummy_data.py       # 테스트 데이터 생성 스크립트
│   ├── db.vuerd.json          # ERD 설계 파일
│   ├── router/                # API 라우터 모듈
│   │   ├── __init__.py
│   │   ├── script_router.py    # 스크립트 관련 API
│   │   ├── movie_router.py     # 영화 관련 API
│   │   ├── actor_router.py     # 배우 관련 API
│   │   └── analysis_router.py  # 영상 분석 API (TMDb 의존성 제거)
│   ├── services/              # 비즈니스 로직 서비스
│   │   ├── __init__.py
│   │   ├── youtube_service.py  # 유튜브 메타데이터 추출
│   │   ├── crawl_service.py    # 배우 이미지 크롤링
│   │   ├── face_service.py     # 얼굴 인식 및 매칭
│   │   └── whisper_service.py  # 음성 전사
│   ├── storage/               # 파일 저장소
│   │   ├── actor_encodings/   # 배우 얼굴 인코딩 파일
│   │   ├── scene_frames/      # 영상 프레임 이미지
│   │   └── audio/             # 추출된 오디오 파일
│   └── venv/                  # Python 가상환경
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

# 배우 이미지 크롤링 API 키 (선택사항)
GOOGLE_API_KEY=your_google_custom_search_api_key_here
GOOGLE_CX=your_google_custom_search_engine_id_here
```

**API 키 발급 방법 (선택사항):**
- **Google Custom Search API**: Google Cloud Console에서 Custom Search API 활성화
- **Google Custom Search Engine**: https://cse.google.com/ 에서 검색 엔진 생성
- **참고**: API 키 없이도 기본 영상 분석 기능은 모두 사용 가능합니다.

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
    title VARCHAR NOT NULL,                   -- 영화 제목
    category VARCHAR,                         -- 카테고리/장르
    youtube_url VARCHAR UNIQUE NOT NULL,      -- YouTube URL (음소거 재생용)
    total_time INTEGER,                       -- 재생시간(분)
    bookmark BOOLEAN DEFAULT FALSE,
    full_background_audio_url VARCHAR         -- 전체 배경음 (더빙 합성용)
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
    movie_id INTEGER NOT NULL,               -- 영화 ID (외래키)
    actor_id INTEGER NOT NULL,               -- 배우 ID (외래키)
    start_time FLOAT NOT NULL,               -- 대사 시작 시간(초)
    end_time FLOAT NOT NULL,                 -- 대사 끝 시간(초)
    script TEXT NOT NULL,                    -- 대사 원문
    translation TEXT,                        -- 대사 번역
    url VARCHAR,                             -- YouTube URL
    actor_pitch_values JSON,                 -- 배우 음성 피치 배열
    background_audio_url VARCHAR,            -- 구간별 배경음 (분석용)
    user_voice_url VARCHAR,                  -- 사용자 더빙 음성
    user_voice_uploaded_at TIMESTAMP,        -- 더빙 업로드 시간
    FOREIGN KEY (movie_id) REFERENCES movies(id),
    FOREIGN KEY (actor_id) REFERENCES actors(id)
);
```

### 🔗 MovieActors 테이블 (관계 테이블)
```sql
CREATE TABLE movie_actors (
    movie_id INTEGER,                        -- 영화 ID
    actor_id INTEGER,                        -- 배우 ID
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

### 🎬 더빙 시스템 아키텍처
- **Movie.youtube_url**: 원본 영상 (프론트에서 음소거 재생)
- **Movie.full_background_audio_url**: 전체 배경음 (더빙 합성용)
- **Script.background_audio_url**: 구간별 배경음 (분석용)
- **Script.user_voice_url**: 사용자 더빙 음성
- **최종 재생**: 유튜브 영상(음소거) + 배경음 + 사용자 음성 = 완성된 더빙작품

## 💡 사용 예시

### 영화 생성
```bash
curl -X POST "http://localhost:8000/movies/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "기생충",
    "category": "드라마",
    "youtube_url": "https://youtube.com/watch?v=example",
    "total_time": 132,
    "full_background_audio_url": "https://s3.amazonaws.com/bucket/parasite_full_bgm.mp3"
    "bookmark": false
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
    "movie_id": 1,
    "actor_id": 1,
    "start_time": 15.5,
    "end_time": 18.2,
    "script": "반지하에서 살고 있습니다",
    "translation": "We live in a semi-basement",
    "url": "https://youtube.com/watch?v=example",
    "actor_pitch_values": [120, 125, 118, 130, 115],
    "background_audio_url": "https://s3.amazonaws.com/bucket/segment_15-18_bg.mp3"
  }'
```

### 사용자 더빙 음성 업로드
```bash
curl -X PUT "http://localhost:8000/scripts/1" \
  -H "Content-Type: application/json" \
  -d '{
    "user_voice_url": "https://s3.amazonaws.com/bucket/user123_script1.mp3"
  }'
```

### 배우별 영화 검색
```bash
curl "http://localhost:8000/movies/actor/송강호"
```

### 영화별 스크립트 조회
```bash
curl "http://localhost:8000/scripts/movie/1"
```

### 카테고리별 영화 검색
```bash
curl "http://localhost:8000/movies/category/로맨스?skip=0&limit=10"
```

### 🎥 YouTube 영상 분석 API 사용 예시

#### 1. 유튜브 메타데이터 추출
```bash
curl -X POST "http://localhost:8000/analysis/youtube/metadata" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=example",
    "movie_title": "기생충"
  }'
```

#### 2. 배우 이미지 크롤링
```bash
curl -X POST "http://localhost:8000/analysis/actors/crawl" \
  -H "Content-Type: application/json" \
  -d '{
    "actors": ["송강호", "최우식", "박소담"],
    "max_images_per_actor": 10
  }'
```

#### 3. 영상 내 얼굴 매칭
```bash
curl -X POST "http://localhost:8000/analysis/face/match" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=example",
    "actors": ["송강호", "최우식"],
    "frame_interval": 30
  }'
```

#### 4. 음성 전사
```bash
curl -X POST "http://localhost:8000/analysis/audio/transcribe" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=example",
    "language": "ko"
  }'
```

#### 5. 전체 분석 파이프라인 실행
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

### ✅ 완료된 작업 항목

#### 🗄️ 데이터베이스 구조 정규화 완료
- **Movie, Actor, Script, MovieActor 모델로 단순화**
- **TMDb 의존성 완전 제거**: tmdb_id, director, release_year, character_name 등 불필요한 필드 삭제
- **외래키 기반 구조**: movie_id, actor_id를 통한 명확한 관계 설정
- **중복 데이터 제거**: 배우 이름 중복 저장 문제 해결

#### 🎥 영상 분석 파이프라인 통합 완료
- **TMDb API 의존성 제거**: 외부 API 없이 독립적인 분석 시스템
- **핵심 기능에 집중**: 유튜브 영상 분석, 얼굴 인식, 음성 전사
- **services/ 구조 정리**: youtube, crawl, face, whisper 서비스 통합
- **analysis_router.py 완전 재작성**: TMDb 관련 코드/엔드포인트 완전 제거

#### 🔧 코드 및 의존성 정리
- **requirements.txt**: TMDb 관련 패키지(tmdbv3api 등) 완전 제거
- **환경변수 정리**: .env에서 TMDB_API_KEY 제거
- **불필요한 서비스 삭제**: services/actor_service.py 제거
- **라우터 정리**: 모든 라우터에서 TMDb 관련 필드/설명 제거

#### 📚 문서 및 예시 업데이트
- **README.md 완전 갱신**: 새로운 DB 구조, API, 사용 예시 반영
- **API 스키마 정리**: schemas.py에서 tmdb_id 등 불필요한 필드 제거
- **일관성 확보**: 코드, 문서, 예시 간의 완전한 일치

### 🎯 프로젝트의 새로운 방향성

#### 핵심 가치
1. **독립성**: 외부 API 의존성 최소화로 안정적인 서비스 제공
2. **단순성**: 복잡한 메타데이터 대신 핵심 기능에 집중
3. **확장성**: 영상 분석 파이프라인의 무한한 확장 가능성

#### 영상 분석 파이프라인
- **유튜브 메타데이터 추출**: 기본 영상 정보 자동 수집
- **배우 이미지 크롤링**: 구글 검색 기반 얼굴 DB 구축
- **실시간 얼굴 매칭**: OpenCV + face_recognition 기반
- **음성 전사**: OpenAI Whisper 기반 고정밀 STT
- **백그라운드 처리**: FastAPI BackgroundTasks로 비동기 작업

#### 현재 API 상태
- **Movie API**: ✅ title, category, youtube_url 기반 단순화
- **Actor API**: ✅ name 기반 고유 배우 관리
- **Script API**: ✅ 외래키 기반 movie_id, actor_id 연결
- **Analysis API**: ✅ TMDb 의존성 완전 제거, 영상 분석 전용

### �️ 기술적 성과

#### 데이터 무결성
- 정규화된 스키마로 데이터 중복 완전 제거
- 외래키 제약조건으로 참조 무결성 보장
- 단순화된 구조로 유지보수성 대폭 향상

#### 서비스 독립성
- 외부 API 장애에 영향받지 않는 안정적인 시스템
- 내부 로직만으로 완전한 기능 제공
- 확장 시에도 외부 의존성 없이 진행 가능

#### 개발 효율성
- 명확한 서비스 분리로 개발/테스트 용이성 증대
- 표준화된 API 구조로 일관된 인터페이스 제공
- 백그라운드 작업으로 사용자 경험 향상

### � 실제 사용 시나리오

```bash
# 1. 영화 생성 (단순화된 구조)
POST /movies/ {"title": "기생충", "category": "드라마", "youtube_url": "..."}

# 2. 배우 추가 (외부 API 없이)
POST /actors/ {"name": "송강호"}

# 3. 영상 분석 파이프라인 실행
POST /analysis/full-analysis {"youtube_url": "...", "movie_title": "기생충"}

# 4. 결과 확인
GET /scripts/movie/1  # 영화별 분석된 스크립트 조회
```

모든 변경사항이 성공적으로 완료되어 **안정적이고 확장 가능한 영상 분석 플랫폼**이 구축되었습니다! 🎉

### 🧹 프로젝트 파일 정리 완료 (2024.06.27)

#### ✅ 중복 파일 제거
- **Models**: `models_new.py`, `models_backup.py` 삭제 → `models.py` 단일 파일 유지
- **Routers**: `analysis_router_new.py`, `script_router_backup.py`, `script_router_new.py` 삭제
- **캐시 파일**: 모든 `__pycache__/` 디렉토리 정리

#### 📝 개발 환경 개선
- **`.gitignore` 생성**: Python, 환경변수, 임시파일, 저장소 파일 무시 설정
- **명확한 구조**: 30개 API 엔드포인트가 정리된 4개 라우터로 체계화
- **일관성 확보**: 모든 파일이 TMDb 제거된 최신 상태로 통일

### 🎤 더빙 시스템 아키텍처 구축 완료 (2024.06.28)

#### ✅ 데이터베이스 스키마 확장
- **Movie 테이블**: `full_background_audio_url` 필드 추가 (전체 배경음 저장)
- **Script 테이블**: `user_voice_url`, `user_voice_uploaded_at` 필드 추가 (사용자 더빙 음성)
- **이중 배경음 구조**: 구간별 분석용 + 전체 합성용으로 효율적 분리

#### � 혁신적인 더빙 재생 방식
- **프론트엔드 처리**: 유튜브 영상(음소거) + 커스텀 오디오 트랙 동시 재생
- **저장 공간 최적화**: 별도 영상 파일 불필요, 유튜브 원본 화질 유지
- **실시간 합성**: 전체 배경음 + 사용자 더빙 음성의 동적 합성

#### 🔄 시스템 플로우
```
1. 영상 분석 → 구간별/전체 배경음 추출
2. 사용자 더빙 → 대사별 음성 녹음 및 저장  
3. 최종 재생 → 유튜브 영상(음소거) + 합성 오디오
4. 결과물 → 완성된 개인 더빙 작품
```

#### �🎯 최종 프로젝트 상태
```
✅ models.py (더빙 기능 포함 확장)
✅ 4개 라우터 (script, movie, actor, analysis)
✅ 4개 서비스 (youtube, crawl, face, whisper)
✅ 30개 API 엔드포인트 정상 작동
✅ TMDb 의존성 완전 제거
✅ .gitignore로 깔끔한 Git 관리
```

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
