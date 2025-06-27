# """
# 영상 분석 관련 API 엔드포인트

# 유튜브 링크 분석, 얼굴 인식, 음성 전사 등의 기능을 제공합니다.
# """

# from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
# from pydantic import BaseModel, HttpUrl
# from typing import List, Optional, Dict
# from sqlalchemy.orm import Session
# import logging

# from database import get_db
# from services.youtube_service import YouTubeService
# from services.crawl_service import CrawlService
# from services.face_service import FaceService
# from services.whisper_service import WhisperService

# logger = logging.getLogger(__name__)

# # API 라우터 설정
# router = APIRouter(
#     prefix="/analysis",
#     tags=["analysis"],
#     responses={404: {"description": "Not found"}}
# )

# # 서비스 인스턴스
# youtube_service = YouTubeService()
# crawl_service = CrawlService()
# face_service = FaceService()
# whisper_service = WhisperService()

# # === Pydantic 스키마 정의 ===

# class YouTubeAnalysisRequest(BaseModel):
#     """유튜브 분석 요청 스키마"""
#     youtube_url: HttpUrl
#     movie_title: str  # 사용자가 직접 입력한 영화 제목

# class YouTubeMetadataResponse(BaseModel):
#     """유튜브 메타데이터 응답 스키마"""
#     title: str
#     description: str
#     tags: List[str]
#     duration: int
#     uploader: str
#     view_count: int
#     video_id: str

# class CrawlRequest(BaseModel):
#     """배우 이미지 크롤링 요청 스키마"""
#     actors: List[str]
#     max_images_per_actor: Optional[int] = 10

# class CrawlResponse(BaseModel):
#     """크롤링 응답 스키마"""
#     status: str
#     message: str
#     results: Dict[str, int]  # 배우별 다운로드된 이미지 수

# class FaceMatchRequest(BaseModel):
#     """얼굴 매칭 요청 스키마"""
#     video_url: HttpUrl
#     actors: List[str]
#     frame_interval: Optional[int] = 30  # 프레임 추출 간격 (초)

# class FaceMatchResponse(BaseModel):
#     """얼굴 매칭 응답 스키마"""
#     status: str
#     message: str
#     matches: Dict[str, List[Dict]]  # 배우별 매칭된 프레임 정보

# class TranscribeRequest(BaseModel):
#     """음성 전사 요청 스키마"""
#     video_url: HttpUrl
#     language: Optional[str] = "ko"  # 언어 코드

# class TranscribeResponse(BaseModel):
#     """음성 전사 응답 스키마"""
#     status: str
#     message: str
#     transcript: str
#     segments: List[Dict]  # 타임스탬프별 구간

# class AnalysisStatusResponse(BaseModel):
#     """분석 상태 응답 스키마"""
#     status: str
#     message: str
#     data: Optional[Dict] = None

# # === API 엔드포인트 ===

# @router.post("/youtube/metadata", response_model=YouTubeMetadataResponse)
# async def extract_youtube_metadata(request: YouTubeAnalysisRequest):
#     """
#     유튜브 URL에서 메타데이터를 추출합니다.
    
#     - **youtube_url**: 분석할 유튜브 비디오 URL
#     - **movie_title**: 사용자가 입력한 영화 제목
#     """
#     try:
#         # URL 유효성 검사
#         url_str = str(request.youtube_url)
#         if not youtube_service.validate_youtube_url(url_str):
#             raise HTTPException(status_code=400, detail="유효하지 않은 유튜브 URL입니다.")
        
#         # 메타데이터 추출
#         metadata = youtube_service.extract_metadata(url_str)
        
#         return YouTubeMetadataResponse(**metadata)
        
#     except Exception as e:
#         logger.error(f"메타데이터 추출 실패: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"메타데이터 추출 중 오류가 발생했습니다: {str(e)}")

# @router.post("/full-analysis", response_model=AnalysisStatusResponse)
# async def start_full_analysis(
#     request: YouTubeAnalysisRequest, 
#     background_tasks: BackgroundTasks,
#     db: Session = Depends(get_db)
# ):
#     """
#     유튜브 영상에 대한 전체 분석을 시작합니다.
    
#     1. 메타데이터 추출
#     2. 영상 분석 및 처리 (백그라운드)
    
#     - **youtube_url**: 분석할 유튜브 비디오 URL
#     - **movie_title**: 사용자가 입력한 영화 제목
#     """
#     try:
#         url_str = str(request.youtube_url)
        
#         # 1. 메타데이터 추출
#         metadata = youtube_service.extract_metadata(url_str)
        
#         # 2. 백그라운드 작업 시작 (추후 구현)
#         # background_tasks.add_task(process_video_analysis, url_str, request.movie_title)
        
#         return AnalysisStatusResponse(
#             status="started",
#             message="분석이 시작되었습니다. 백그라운드에서 처리됩니다.",
#             data={
#                 "metadata": metadata,
#                 "movie_title": request.movie_title
#             }
#         )
        
#     except Exception as e:
#         logger.error(f"전체 분석 시작 실패: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"분석 시작 중 오류가 발생했습니다: {str(e)}")

# @router.post("/actors/crawl", response_model=CrawlResponse)
# async def crawl_actor_images(
#     request: CrawlRequest,
#     background_tasks: BackgroundTasks
# ):
#     """
#     배우 이미지를 크롤링합니다.
    
#     - **actors**: 크롤링할 배우 이름 목록
#     - **max_images_per_actor**: 배우당 최대 이미지 수 (기본: 10)
#     """
#     try:
#         # 배경 작업으로 크롤링 실행
#         def crawl_task():
#             results = {}
#             for actor in request.actors:
#                 try:
#                     downloaded_count = crawl_service.crawl_actor_images(
#                         actor, 
#                         max_images=request.max_images_per_actor
#                     )
#                     results[actor] = downloaded_count
#                     logger.info(f"배우 {actor}: {downloaded_count}개 이미지 크롤링 완료")
#                 except Exception as e:
#                     logger.error(f"배우 {actor} 크롤링 실패: {str(e)}")
#                     results[actor] = 0
#             return results
        
#         background_tasks.add_task(crawl_task)
        
#         return CrawlResponse(
#             status="started",
#             message=f"{len(request.actors)}명의 배우 이미지 크롤링을 시작했습니다.",
#             results={actor: 0 for actor in request.actors}  # 초기값
#         )
        
#     except Exception as e:
#         logger.error(f"크롤링 시작 실패: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"크롤링 시작 중 오류가 발생했습니다: {str(e)}")

# @router.post("/face/match", response_model=FaceMatchResponse)
# async def match_faces_in_video(
#     request: FaceMatchRequest,
#     background_tasks: BackgroundTasks
# ):
#     """
#     비디오에서 배우 얼굴을 매칭합니다.
    
#     - **video_url**: 분석할 비디오 URL
#     - **actors**: 매칭할 배우 목록
#     - **frame_interval**: 프레임 추출 간격 (초, 기본: 30)
#     """
#     try:
#         url_str = str(request.video_url)
        
#         # 배경 작업으로 얼굴 매칭 실행
#         def face_match_task():
#             matches = {}
#             try:
#                 # 1. 비디오에서 프레임 추출
#                 frames = face_service.extract_frames_from_video(
#                     url_str, 
#                     interval=request.frame_interval
#                 )
                
#                 # 2. 각 배우별로 얼굴 매칭
#                 for actor in request.actors:
#                     actor_matches = face_service.match_faces_in_frames(actor, frames)
#                     matches[actor] = actor_matches
#                     logger.info(f"배우 {actor}: {len(actor_matches)}개 매칭 완료")
                
#             except Exception as e:
#                 logger.error(f"얼굴 매칭 실패: {str(e)}")
                
#             return matches
        
#         background_tasks.add_task(face_match_task)
        
#         return FaceMatchResponse(
#             status="started",
#             message=f"비디오에서 {len(request.actors)}명의 배우 얼굴 매칭을 시작했습니다.",
#             matches={actor: [] for actor in request.actors}  # 초기값
#         )
        
#     except Exception as e:
#         logger.error(f"얼굴 매칭 시작 실패: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"얼굴 매칭 시작 중 오류가 발생했습니다: {str(e)}")

# @router.post("/audio/transcribe", response_model=TranscribeResponse)
# async def transcribe_audio(
#     request: TranscribeRequest,
#     background_tasks: BackgroundTasks
# ):
#     """
#     비디오에서 음성을 추출하고 텍스트로 변환합니다.
    
#     - **video_url**: 분석할 비디오 URL
#     - **language**: 언어 코드 (기본: ko)
#     """
#     try:
#         url_str = str(request.video_url)
        
#         # 배경 작업으로 음성 전사 실행
#         def transcribe_task():
#             try:
#                 # 1. 비디오에서 오디오 추출
#                 audio_path = whisper_service.extract_audio_from_video(url_str)
                
#                 # 2. 음성을 텍스트로 변환
#                 transcript, segments = whisper_service.transcribe_audio(
#                     audio_path, 
#                     language=request.language
#                 )
                
#                 logger.info(f"음성 전사 완료: {len(segments)}개 구간")
#                 return transcript, segments
                
#             except Exception as e:
#                 logger.error(f"음성 전사 실패: {str(e)}")
#                 return "", []
        
#         background_tasks.add_task(transcribe_task)
        
#         return TranscribeResponse(
#             status="started",
#             message="음성 추출 및 전사를 시작했습니다.",
#             transcript="",  # 초기값
#             segments=[]     # 초기값
#         )
        
#     except Exception as e:
#         logger.error(f"음성 전사 시작 실패: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"음성 전사 시작 중 오류가 발생했습니다: {str(e)}")

# @router.get("/health")
# async def analysis_health_check():
#     """분석 서비스 상태 확인"""
#     return {"status": "healthy", "service": "analysis", "message": "분석 서비스가 정상 작동 중입니다."}
