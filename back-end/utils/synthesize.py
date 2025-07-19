# step1_get_scripts.py
from sqlalchemy.orm import Session
from models import Script
from pydub import AudioSegment
from router.utils_s3 import load_user_audio_from_s3, upload_audio_to_s3

import os
import re


def extract_youtube_video_id(url: str) -> str:

    match = re.search(r"(?:youtu\.be/|v=)([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    raise ValueError(f"❌ 유효한 YouTube URL 아님: {url}")


def get_token_info(session: Session, token_id: int):
    from models import Token
    token = session.query(Token).filter(Token.id == token_id).first()
    if token is None:
        raise ValueError(f"❌ token_id={token_id}에 해당하는 Token이 없습니다.")

    actor_name = token.actor_name
    youtube_url = token.youtube_url

    # YouTube ID 추출
    video_id = extract_youtube_video_id(youtube_url)
    start_time = token.start_time  # 추가

    return actor_name, video_id, start_time
    

def get_scripts_by_token(session: Session, token_id: int):
    scripts = (
        session.query(Script)
        .filter(Script.token_id == token_id)
        .order_by(Script.id)
        .all()
    )

    return scripts


def prepare_dub_segments(user_id: int, token_id: int, scripts: list,  token_start_time: float) -> list[dict]:
    segments = []

    for script in scripts:
        audio = load_user_audio_from_s3(user_id, token_id, script.id)
        if audio is None:
            continue

        segments.append({
            # 절대 시간 기준을 만들기 위해서 필요함
            "start": script.start_time - token_start_time,
            "end": script.end_time - token_start_time,
            "audio": audio  # 경로가 아닌 실제 AudioSegment
        })

    return segments



def synthesize_audio_from_segments(
    background: AudioSegment, 
    original: AudioSegment, 
    segments: list, 
    user_id: int, 
    token_id: int
) -> str:
    result = background[:]

    # 1. 내 음성 덮어쓰기
    for seg in segments:
        start_ms = int(seg["start"] * 1000)
        end_ms = int(seg["end"] * 1000)
        print(f"🎤 내 더빙 구간: {seg['start']}s ~ {seg['end']}s")

        # 원본 오디오의 해당 부분을 먼저 잘라내고, 그 다음에 사용자 음성을 오버레이합니다.
        # 이 방식은 원본의 소리를 완전히 대치합니다.
        result = result.overlay(AudioSegment.silent(duration=end_ms - start_ms), position=start_ms)
        result = result.overlay(seg["audio"], position=start_ms)

    # 2. 상대방 음성(원본 보컬) 삽입
    print("🗣️ 상대방 음성 덮어쓰기 중...")
    
    current_position_ms = 0
    for seg in sorted(segments, key=lambda x: x['start']):
        start_ms = int(seg["start"] * 1000)
        end_ms = int(seg["end"] * 1000)

        # 현재 위치와 내 더빙 시작점 사이에 비어있는 공간(상대방 목소리)을 원본으로 채웁니다.
        if current_position_ms < start_ms:
            original_part = original[current_position_ms:start_ms]
            result = result.overlay(original_part, position=current_position_ms)
        
        current_position_ms = end_ms

    # 마지막 더빙 이후의 남은 부분을 원본으로 채웁니다.
    if current_position_ms < len(original):
        remaining_part = original[current_position_ms:]
        result = result.overlay(remaining_part, position=current_position_ms)

    # S3에 업로드하고 S3 키를 반환
    s3_key = upload_audio_to_s3(result, user_id, token_id)
    
    return s3_key
