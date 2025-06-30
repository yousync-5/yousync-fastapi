
```markdown
# FastAPI 백엔드 학습 및 발표 자료

이 문서는 현재 FastAPI 기반 백엔드 프로젝트의 구성과 핵심 기능을 설명합니다.  
실제 코드를 공부하고, 발표 자료로 활용할 수 있도록 **핵심 포인트**를 정리했습니다.

---

## 1. 프로젝트 구조

```
/fast-api
 ├── back-end
 │    ├── main.py
 │    ├── models.py
 │    ├── database.py
 │    ├── router
 │    │    ├── user_audio_router.py
 │    │    ├── script_router.py
 │    │    ├── token_router.py
 │    │    └── ...
 │    ├── celery_app.py (과거 Celery 사용 시)
 │    ├── ...
 └── ...
```

- **main.py**: FastAPI 앱 생성, 라우터 등록, DB 초기화.  
- **models.py**: SQLAlchemy ORM 모델 정의.  
- **database.py**: DB 연결(엔진, 세션), `get_db()` 세션 종속성.  
- **router** 폴더: API 라우팅 모음 (예: user_audio_router.py).  
- **celery_app.py**: 과거 비동기 처리를 Celery로 구현할 때 사용(현재는 httpx 비동기로 대체).

---

## 2. 핵심 파일별 요약

### 2.1 main.py

- FastAPI 앱 생성.  
- CORS 미들웨어 설정(allow_origins=["*"]).  
- `Base.metadata.create_all(bind=engine)`로 DB 테이블 자동 생성(개발 편의).  
- 여러 라우터를 `app.include_router(...)`로 등록.

### 2.2 user_audio_router.py

- 오디오 파일 업로드 → S3 저장 → 분석 서버로 비동기 요청 → 결과 웹훅을 수신.  
- **핵심 포인트**  
  1) [비동기 S3 업로드] → `upload_to_s3_async()`  
  2) [분석서버 요청] → `send_analysis_request_async()` (httpx.AsyncClient 사용)  
  3) [메모리 저장소] → `analysis_store[job_id]`로 진행 상황 추적  
  4) [SSE(Server-Sent Events)] → `/analysis-progress/{job_id}` 엔드포인트로 실시간 진행 상황 전송  

예) SSE 사용 시 프론트엔드에서:
```js
const jobId = "1234";
const es = new EventSource(`/tokens/analysis-progress/${jobId}`);
es.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("진행 상황:", data);
  if (data.status === "completed" || data.status === "failed") {
    es.close();
  }
};
```
이렇게 하면 일정 주기로 백엔드에서 진행 상황을 push해 준다.

### 2.3 기타 주요 요소

- **boto3**: S3 업로드/다운로드 관리.  
- **analysis_store**(dict): 메모리 상에 job 상태 보관. 개발·테스트엔 편리하나, 다중 서버 환경에선 Redis/DB를 사용해야 안전.  
- **webhook**: 분석 서버가 최종 결과를 POST해 주면 `/webhook/analysis-complete`에서 수신 후 `analysis_store` 갱신.

---

## 3. 구현 흐름 (발표 자료용)

1) **유저 요청**: `/tokens/{token_id}/upload-audio`  
   - 파일 수신(UploadFile) → job_id 생성 → `analysis_store[job_id]`에 초기 상태 기록.  
   - FastAPI의 `BackgroundTasks`로 실제 업로드·분석요청 작업을 비동기로 수행.  
2) **비동기 작업**:  
   - S3 업로드(`upload_to_s3_async`) 후, 분석 서버에 httpx 비동기 POST(`send_analysis_request_async`).  
   - 분석 서버는 완료 후 웹훅 콜백을 `webhook_url=?job_id=...`에 전송.  
3) **결과 수신**: `/tokens/webhook/analysis-complete`  
   - job_id를 통해 `analysis_store`에 상태=“completed”로 갱신.  
4) **SSE 진행 상황**:  
   - `/analysis-progress/{job_id}`로 Server-Sent Events 엔드포인트를 열면, 1초 간격으로 `analysis_store[job_id]` 정보를 실시간 전송.  
   - 클라이언트 브라우저에서 EventSource로 수신 가능.

---

## 4. 확장 및 공부 포인트

1) **In-Memory vs Redis/DB**  
   - 현재 `analysis_store`는 파이썬 dict이므로 서버 재시작 시 데이터 소실.  
   - 확장 운영 시 Redis나 DB 테이블에 job 상태를 저장하는 것이 베스트 프랙티스.  
2) **Celery vs BackgroundTasks**  
   - 과거에는 Celery+Redis로 분산 처리.  
   - 지금은 httpx 비동기로 간소화했지만, 대규모 트래픽·고용량 파일이라면 Celery/RQ/Huey 같은 워커 시스템을 다시 검토.  
3) **보안**  
   - S3 업로드 시 AWS 자격 증명 보호, `.env` 파일 .gitignore 처리.  
   - HTTPS 사용, CORS 도메인 제한 등 프로덕션 환경에서 필수 고려.  
4) **회원가입/로그인**  
   - 필요 시 `auth_router.py` 등으로 JWT 또는 세션 기반 로그인을 구현 가능.  
   - 비밀번호 해싱(passlib), DB User 모델 등을 함께 학습.

---

## 5. 마무리

이 저장소는 **FastAPI**와 **비동기 httpx**, **S3