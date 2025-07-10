from fastapi import FastAPI, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from datetime import datetime
import time
from urllib.parse import urlparse
import uuid
import boto3
import tempfile
import json
import numpy as np
import shutil
import requests
from pathlib import Path
from run_whisper_cpp import speech_to_text
from text_similarity import compare_texts
from sklearn.metrics.pairwise import cosine_similarity
from mfcc_similarity import extract_mfcc_from_audio, extract_mfcc_segment, compare_mfcc_segments

import threading  # ← 이 줄 추가
import asyncio   # ← 이 줄 추가

# 수정 전
# app = FastAPI(
#     title = "Voice Analysis API",
#     description = "유저 음성 분석 및 평가 자동화 API")

# 수정 후 
app = FastAPI(
    title = "Voice Analysis API",
    description = "유저 음성 분석 및 평가 자동화 API")

# SQS 설정 추가
SQS_QUEUE_URL = 'https://sqs.ap-northeast-2.amazonaws.com/975049946580/audio-analysis-queue'
sqs_client = boto3.client('sqs', region_name='ap-northeast-2')

# 작업 상태 저장 딕셔너리
job_status = {}

# 작업 상태 저장 딕셔너리
job_status = {}

@app.get("/")
async def root():
    return {"message" : "Voice Analysis API", "status" : "running"}

@app.get("/status")
async def server_status():
    return {
        "status" : "running",
        "timestamp" : datetime.now().isoformat(),
        "message" : "Voice Analysis API 정상 작동 중"
    }

@app.post("/analyze-voice")
async def analyze_voice(
    background_tasks: BackgroundTasks,
    request_data: str = Form(...)
):
    # 고유한 job_id 생성
    job_id = str(uuid.uuid4())

    # 시작 시간 기록
    start_time = time.time()
    start_datetime = datetime.now()
    print(f"[{job_id}] 🚀 요청 시작: {start_datetime}")
    data = json.loads(request_data)
    s3_audio_url = data["s3_audio_url"]
    webhook_url = data["webhook_url"]
    script_data = data["script"]

    try:
        # S3 URL에서 키 추출
        #bucket, s3_key = parse_s3_url(s3_audio_url)

        # 작업 상태 초기화
        job_status[job_id] = {
            "status": "processing",
            "s3_audio_url": s3_audio_url,
            "started_at": datetime.now().isoformat()
        }

        audio_path = download_from_s3(s3_audio_url, job_id)

        #백그라운드에서 처리
        background_tasks.add_task(analyze_pronunciation_pipeline, job_id, audio_path, script_data, s3_audio_url, webhook_url, start_time)

        return {
            "job_id": job_id,
            "status": "processing",
            "message": "음성 분석이 시작되었습니다."
            }
    
    except ValueError as e :
        # 사용자 요청이 잘못된 경우 -> 400
        job_status[job_id] = {
            "status": "failed",
            "s3_audio_url": s3_audio_url,
            "started_at": datetime.now().isoformat(),
            "error": str(e)
        }
        return JSONResponse(
            status_code=400,
            content={"error": f"잘못된 요청: {str(e)}"}
            )
    
    except Exception as e :
        # 그 외의 예외는 서버 내부 오류 -> 500
        job_status[job_id] = {
            "status": "failed",
            "s3_audio_url": s3_audio_url,
            "started_at": datetime.now().isoformat(),
            "error": str(e)
        }
        return JSONResponse(
            status_code=500,
            content={"error": f"서버 오류: {str(e)}"}
            )
    
def parse_s3_url(s3_url: str) -> tuple[str, str]:
    if s3_url.startswith('s3://'):
        # s3://bucket/key 형태
        parts = s3_url.split('/', 3)
        if len(parts) < 4:
            raise ValueError("올바른 s3://bucket/key 형식이 아닙니다.")
        return parts[2], parts[3]
    
    elif 'amazonaws.com' in s3_url:
        # https://bucket.s3.amazonaws.com/key 형태
        parsed = urlparse(s3_url)
        netloc_parts = parsed.netloc.split('.')
        if len(netloc_parts) < 3 or not parsed.path:
            raise ValueError("올바르지 않은 S3 URL 형식입니다.")
        bucket = netloc_parts[0]
        key = parsed.path.lstrip('/')
        return bucket, key
    else:
        raise ValueError("지원되지 않은 S3 URL 형식입니다.")

def download_from_s3(s3_audio_url: str, job_id: str) -> str:
    #S3 클라이언트 생성
    s3_client = boto3.client('s3')

    audio_bucket, audio_key = parse_s3_url(s3_audio_url)

    # job_id 기반 고유 경로 생성
    job_folder = Path(f"/tmp/{job_id}")
    job_folder.mkdir(exist_ok=True)

    # 파일 다운로드 경로 생성 및 유저 음성 다운로드
    audio_path = job_folder / "user_audio.wav"
    s3_client.download_file(audio_bucket, audio_key, str(audio_path))

    return str(audio_path)

async def analyze_pronunciation_pipeline(job_id: str, audio_path: str, script_data: dict, s3_audio_url: str, webhook_url: str, start_time: float):
    """
    1. user 음성을 STT로
    2. 기준 음성 캐시 데이터 load
    3. 텍스트 비교
    4. mfcc 비교
    5. 종합 점수 계산
    6. 결과 저장 -> json
    """
    
    try:
        # step1: user 음성 -> STT
        print(f"[{job_id}] step1: user 음성을 STT로 변환 중")
        output_dir = Path(audio_path).parent
        model_path = Path("./whisper.cpp/models/ggml-tiny.en.bin")  # 현재는 tiny 모델

        user_stt_result = speech_to_text(audio_path=Path(audio_path), output_dir=output_dir, model_path=model_path)
        print(f"[{job_id}] user 음성 -> STT 변환 완료")




        # step2: 기준 음성 스크립트 데이터 load
        print(f"[{job_id}] step2: 기준 음성 스크립트 데이터 로딩 중")
        reference_script = script_data

        # 캐시 데이터 검증 ❌❌❌❌❌ 변수명은 임의로 정함 ❌❌❌❌❌
        if 'words' not in reference_script:
            raise ValueError("캐시 파일에 words가 없습니다")
        print(f"[{job_id}] step2: 기준 음성 스크립트 데이터 로딩 완료")


        
        # step3: 텍스트 비교
        print(f"[{job_id}] step3: 기준 음성 <-> 유저 음성 텍스트 비교")

        """
        🌹🌹🌹🌹🌹 아래는 whisper.cpp 모델의 출력 옵션인 -oj(json으로 출력)의 표준 json 구조임 🌹🌹🌹🌹🌹
        
        json
    {
    "systeminfo": "...",
    "model": {...},
    "params": {...},
    "result": {...},
    "transcription": [
        {
        "timestamps": {...},
        "offsets": {...},
        "text": " There's a lot of overlap in their philosophies.",
        "tokens": [...]
        }
    ]
    }
        """

        # user STT 결과에서 텍스트 추출
        user_text = ""
        if user_stt_result.get('transcription'):                                        # 해당 키가 있으면
            user_text = user_stt_result['transcription'][0].get('text', '').strip()     # 추출
        
        # 기준 음성 스크립트 데이터에서 단어 리스트들 추출
        reference_words = []
        for word_data in reference_script['words']:                        # 기준 음성 캐시 JSON 파일의 단어 단위 세그먼트 리스트. 'segment' 라는 이름은 임의임.
            reference_words.append(word_data['word'])                       # segment['word']는 해당 단어의 정보를 담은 dic

        # 텍스트 비교 실행
        text_comparison_result = compare_texts(reference_words, user_text)
        print(f"[{job_id}] step3: 기준 음성 <-> 유저 음성 텍스트 비교 완료")



        # step4: 기준 음성 <-> 유저 음성 mfcc 비교
        print(f"[{job_id}] step4: 기준 음성 <-> 유저 음성 mfcc 비교")

        # 유저 음성에서 mfcc 추출
        user_mfcc, user_frame_times = extract_mfcc_from_audio(audio_path)

        # 기준 캐시에서 mfcc 데이터 로드
        reference_words_data = reference_script['words']   # 기준 음성 캐시 JSON 파일의 단어 단위 리스트.

        # 캐시된 세그먼트와 사용자 mfcc 비교
        mfcc_comparison_result = compare_mfcc_segments(cached_segments=reference_script['words'], user_mfcc=user_mfcc, user_frame_times=user_frame_times)
        print(f"[{job_id}] step4: 기준 음성 <-> 유저 음성 mfcc 비교 완료")



        # step5: 종합 점수 계산
        print(f"[{job_id}] step5: 단어별 통합 결과 생성")

        # 단어별 통합 결과 생성
        word_analysis = []
        text_pass_count = 0

        for i, word in enumerate(reference_words):
            # 텍스트 결과 가져오기
            text_status = text_comparison_result[i]["status"] if i < len(text_comparison_result) else "fail"
            
            # MFCC 결과 가져오기  
            word_data = reference_script['words'][i]
            if word_data['mfcc'] is not None:
                mfcc_similarity = mfcc_comparison_result[i]["similarity"] if i < len(mfcc_comparison_result) else 0.0
            else:
                mfcc_similarity = 0.0
            
            # 단어별 종합 점수 계산 (텍스트 6할 + MFCC 4할)
            text_score = 1.0 if text_status == "pass" else 0.0
            word_score = (text_score * 0.6) + (mfcc_similarity * 0.4)
            
            # 통합 결과 추가
            word_analysis.append({
                "word": word,
                "text_status": text_status,
                "mfcc_similarity": round(mfcc_similarity, 3),
                "word_score": round(word_score, 3)
            })
            
            # 텍스트 통과 개수 계산
            if text_status == "pass":
                text_pass_count += 1

        # 전체 요약 계산
        text_accuracy = text_pass_count / len(reference_words) if reference_words else 0.0

        # MFCC 평균 계산
        mfcc_total = 0.0
        for result in word_analysis:
            mfcc_total += result["mfcc_similarity"]
        mfcc_average = mfcc_total / len(word_analysis) if word_analysis else 0.0

        # 전체 점수 계산
        score_total = 0.0
        for result in word_analysis:
            score_total += result["word_score"]
        overall_score = score_total / len(word_analysis) if word_analysis else 0.0

        print(f"[{job_id}] 통합 결과 생성 완료 - 전체 점수: {overall_score:.3f}")

        # 통합된 결과 구조
        detailed_results = {
            "overall_score": round(overall_score, 3),
            "word_analysis": word_analysis,
            "summary": {
                "text_accuracy": round(text_accuracy, 3),
                "mfcc_average": round(mfcc_average, 3),
                "total_words": len(reference_words),
                "passed_words": text_pass_count
            }
        }
        # step6: 결과 저장
        print(f"[{job_id}] step6: 결과 저장 중")

        # # 성공적으로 완료된 작업 상태 업데이트
        # job_status[job_id] = {
        #     "status": "completed",
        #     "result": detailed_results,
        #     "s3_audio_url": s3_audio_url,
        #     "started_at": job_status[job_id]["started_at"],
        #     "completed_at": datetime.now().isoformat()
        # }

        # 웹훅 시작 시간 기록
        webhook_start = time.time()
        print(f"[{job_id}] 웹훅 호출 중: {webhook_url}")
        webhook_response = requests.post(webhook_url, json={
            "job_id": job_id,
            "status": "completed",
            "result": detailed_results
        }, timeout=10)
        print(f"[{job_id}] 웹훅 호출 완료: {webhook_response.status_code}")
        # 시간 계산
        webhook_end = time.time()
        total_end = time.time()
        webhook_duration = webhook_end - webhook_start
        total_duration = total_end - start_time
        print(f"[{job_id}] ⏱️ 웹훅 전송 시간: {webhook_duration:.2f}초")
        print(f"[{job_id}] 🏁 전체 처리 시간: {total_duration:.2f}초 (요청 → 웹훅 완료)")

    except Exception as e:
        print(f"[{job_id}] 파이프라인 에러 발생: {str(e)}")

        # 실패 시 웹훅
        try:
            # 실패 웹훅 시작 시간
            webhook_start = time.time()
            print(f"[{job_id}] 실패 웹훅 호출 중: {webhook_url}")
            requests.post(webhook_url, json={
                "job_id": job_id,
                "status": "failed",
                "error": str(e)
            }, timeout=10)
            print(f"[{job_id}] 실패 웹훅 호출 완료: {webhook_url}")
            # 실패 시 시간 계산
            webhook_end = time.time()
            total_end = time.time()
            webhook_duration = webhook_end - webhook_start
            total_duration = total_end - start_time
            print(f"[{job_id}] ⏱️ 웹훅 전송 시간: {webhook_duration:.2f}초")
            print(f"[{job_id}] 🏁 전체 처리 시간: {total_duration:.2f}초 (요청 → 웹훅 완료)")
        except Exception as webhook_error:
            print(f"[{job_id}] 웹훅 호출 실패: {webhook_error}")


    finally:
        try:
            job_folder = Path(audio_path).parent
            shutil.rmtree(job_folder)
            print(f"[{job_id}] 임시 파일 정리 완료")
        except Exception as cleanup_error:
                print(f"[{job_id}] 임시 파일 정리 실패: {cleanup_error}")

########################추가 함수
def sqs_message_processor():
    """SQS에서 메시지를 받아서 처리하는 함수"""
    print("🔄 SQS 메시지 처리 시작...")
    
    while True:
        try:
            response = sqs_client.receive_message(
                QueueUrl=SQS_QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20
            )
            
            messages = response.get('Messages', [])
            for message in messages:
                print(f"📨 SQS 메시지 수신: {message['MessageId']}")
                
                # 메시지 처리
                process_sqs_message(message)
                
                # 메시지 삭제
                sqs_client.delete_message(
                    QueueUrl=SQS_QUEUE_URL,
                    ReceiptHandle=message['ReceiptHandle']
                )
                print(f"✅ SQS 메시지 처리 완료: {message['MessageId']}")
                
        except Exception as e:
            print(f"❌ SQS 처리 오류: {e}")
            time.sleep(5)

def process_sqs_message(message):
    """SQS 메시지를 파싱하여 분석 실행"""
    try:
        # 메시지 파싱
        body = json.loads(message['Body'])
        
        job_id = body['job_id']
        s3_audio_url = body['s3_audio_url']
        webhook_url = body['webhook_url']
        video_id = body.get('video_id', 'unknown')
        
        print(f"🎯 SQS 분석 시작 - Job ID: {job_id}")
        
        # 스크립트 데이터 준비
        script_data = get_script_data_by_video_id(video_id)
        
        # 기존 분석 파이프라인 실행
        start_time = time.time()
        audio_path = download_from_s3(s3_audio_url, job_id)
        
        # 비동기 함수를 동기적으로 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            analyze_pronunciation_pipeline(
                job_id, audio_path, script_data, s3_audio_url, webhook_url, start_time
            )
        )
        loop.close()
        
    except Exception as e:
        print(f"❌ SQS 메시지 처리 실패: {e}")
        # 실패 시에도 웹훅 전송
        try:
            requests.post(webhook_url, json={
                "job_id": body.get('job_id', 'unknown'),
                "status": "failed",
                "error": str(e)
            }, timeout=10)
        except Exception as webhook_error:
            print(f"❌ 실패 웹훅 전송 실패: {webhook_error}")

def get_script_data_by_video_id(video_id: str) -> dict:
    """video_id로 스크립트 데이터 조회"""
    print(f"📋 스크립트 데이터 조회 - video_id: {video_id}")
    
    # TODO: 실제 데이터로 교체 필요
    return {
        "words": [
            {"word": "hello", "mfcc": None},
            {"word": "world", "mfcc": None},
            {"word": "test", "mfcc": None}
        ]
    }

#####################추가함

@app.on_event("startup")
async def startup_event():
    """FastAPI 서버 시작 시 SQS 처리 스레드 시작"""
    print("🚀 FastAPI 서버 시작")
    print("🔄 SQS 메시지 처리 스레드 시작...")
    
    sqs_thread = threading.Thread(target=sqs_message_processor, daemon=True)
    sqs_thread.start()
    
    print("✅ SQS 처리 스레드 시작 완료")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("pronunciation:app", host="0.0.0.0", port=8001, reload=False)


