# step1_get_scripts.py
from sqlalchemy.orm import Session
from models import Script
from pydub import AudioSegment
from router.utils_s3 import load_user_audio_from_s3

import os
import re

def extract_youtube_video_id(url: str) -> str:
    # https://youtu.be/abc123XYZ
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

    return actor_name, video_id
    

def get_scripts_by_token(session: Session, token_id: int):
    scripts = (
        session.query(Script)
        .filter(Script.token_id == token_id)
        .order_by(Script.id)
        .all()
    )

    return scripts


def prepare_dub_segments(user_id: int, token_id: int, scripts: list) -> list[dict]:
    segments = []

    for script in scripts:
        audio = load_user_audio_from_s3(user_id, token_id, script.id)
        if audio is None:
            continue

        segments.append({
            "start": script.start_time,
            "end": script.end_time,
            "audio": audio  # 경로가 아닌 실제 AudioSegment
        })

    return segments



def synthesize_audio_from_segments(background: AudioSegment, original: AudioSegment, segments: list):
    result = background[:]

    # 1. 내 음성 덮어쓰기
    for seg in segments:
        start_ms = int(seg["start"] * 1000)
        end_ms = int(seg["end"] * 1000)
        print(f"🎤 내 더빙 구간: {seg['start']}s ~ {seg['end']}s")

        result = result.overlay(AudioSegment.silent(duration=end_ms - start_ms), position=start_ms)
        result = result.overlay(seg["audio"], position=start_ms)

    # 2. 상대방 음성 삽입
    print("🗣️ 상대방 음성 덮어쓰기 중...")

    current = 0
    for seg in segments:
        start_ms = int(seg["start"] * 1000)
        if current < start_ms:
            part = original[current:start_ms]
            result = result.overlay(part, position=current)
        current = int(seg["end"] * 1000)

    if current < len(original):
        part = original[current:]
        result = result.overlay(part, position=current)

    result.export("final_mix.wav", format="wav")
    print("✅ 합성 완료 → final_mix.wav 저장됨")