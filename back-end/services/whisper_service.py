"""
음성 전사 서비스

YouTube 영상에서 오디오를 추출하고 Whisper를 사용하여 자막을 생성합니다.
"""

import os
import subprocess
import whisper_timestamped as whisper
import torch
from pytube import YouTube
import yt_dlp
from typing import Dict, List, Optional, Tuple
import logging
import json

logger = logging.getLogger(__name__)

class WhisperService:
    def __init__(self, base_dir: str = "storage"):
        """
        음성 전사 서비스 초기화
        
        Args:
            base_dir (str): 기본 저장 디렉토리
        """
        self.base_dir = base_dir
        self.audio_dir = os.path.join(base_dir, "audio")
        self.subtitle_dir = os.path.join(base_dir, "subtitles")
        
        # 디렉토리 생성
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.subtitle_dir, exist_ok=True)
        
        # Whisper 모델 (처음 사용시 다운로드)
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"🎵 Whisper 서비스 초기화 (디바이스: {self.device})")
    
    def _load_whisper_model(self, model_size: str = "base") -> None:
        """
        Whisper 모델을 로드합니다.
        
        Args:
            model_size (str): 모델 크기 (tiny, base, small, medium, large)
        """
        try:
            if self.model is None:
                logger.info(f"🤖 Whisper {model_size} 모델 로딩 중...")
                self.model = whisper.load_model(model_size, device=self.device)
                logger.info(f"✅ Whisper 모델 로드 완료")
        except Exception as e:
            logger.error(f"❌ Whisper 모델 로드 실패: {str(e)}")
            raise
    
    def download_audio_from_youtube(self, url: str, filename: Optional[str] = None) -> str:
        """
        YouTube 영상에서 오디오를 추출합니다.
        
        Args:
            url (str): YouTube URL
            filename (str, optional): 저장할 파일명 (없으면 video_id 사용)
            
        Returns:
            str: 저장된 오디오 파일 경로
        """
        try:
            # 파일명 설정
            if filename is None:
                video_id = YouTube(url).video_id
                filename = video_id
            
            output_template = os.path.join(self.audio_dir, f"{filename}.%(ext)s")
            
            # yt-dlp 설정
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }
            
            logger.info(f"📥 오디오 다운로드 시작: {url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                
            audio_path = os.path.join(self.audio_dir, f"{filename}.mp3")
            
            if os.path.exists(audio_path):
                logger.info(f"✅ 오디오 다운로드 완료: {audio_path}")
                return audio_path
            else:
                raise Exception("오디오 파일이 생성되지 않았습니다")
                
        except Exception as e:
            logger.error(f"❌ 오디오 다운로드 실패: {str(e)}")
            raise Exception(f"오디오 다운로드 중 오류가 발생했습니다: {str(e)}")
    
    def transcribe_audio(self, audio_path: str, output_name: Optional[str] = None, 
                        model_size: str = "base") -> Dict:
        """
        오디오 파일을 전사하여 자막을 생성합니다.
        
        Args:
            audio_path (str): 오디오 파일 경로
            output_name (str, optional): 출력 파일명
            model_size (str): Whisper 모델 크기
            
        Returns:
            Dict: 전사 결과 (세그먼트 정보 포함)
        """
        try:
            if not os.path.exists(audio_path):
                raise Exception(f"오디오 파일이 존재하지 않습니다: {audio_path}")
            
            # Whisper 모델 로드
            self._load_whisper_model(model_size)
            
            if output_name is None:
                output_name = os.path.splitext(os.path.basename(audio_path))[0]
            
            logger.info(f"🎙️ 음성 전사 시작: {audio_path}")
            
            # 오디오 로드 및 언어 감지
            audio = whisper.load_audio(audio_path)
            detected_lang = whisper.detect_language(self.model, audio)
            
            logger.info(f"🌐 감지된 언어: {detected_lang}")
            
            # 전사 실행
            result = whisper.transcribe(self.model, audio_path, language=detected_lang)
            
            # SRT 자막 파일 생성
            srt_path = self._save_srt_subtitle(result, output_name)
            
            # JSON 결과 파일 생성
            json_path = self._save_json_result(result, output_name)
            
            # 결과 정리
            transcription_result = {
                "success": True,
                "detected_language": detected_lang,
                "total_segments": len(result.get("segments", [])),
                "duration": result.get("duration", 0),
                "srt_file": srt_path,
                "json_file": json_path,
                "segments": result.get("segments", [])
            }
            
            logger.info(f"✅ 음성 전사 완료: {len(result.get('segments', []))}개 세그먼트")
            
            return transcription_result
            
        except Exception as e:
            logger.error(f"❌ 음성 전사 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def transcribe_youtube_url(self, url: str, filename: Optional[str] = None,
                              model_size: str = "base") -> Dict:
        """
        YouTube URL에서 직접 음성을 전사합니다.
        
        Args:
            url (str): YouTube URL
            filename (str, optional): 파일명
            model_size (str): Whisper 모델 크기
            
        Returns:
            Dict: 전사 결과
        """
        try:
            # 1. 오디오 다운로드
            audio_path = self.download_audio_from_youtube(url, filename)
            
            # 2. 음성 전사
            result = self.transcribe_audio(audio_path, filename, model_size)
            
            # 3. 오디오 파일 정리 (옵션)
            # os.remove(audio_path)  # 용량 절약을 위해 삭제 가능
            
            return result
            
        except Exception as e:
            logger.error(f"❌ YouTube 음성 전사 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _save_srt_subtitle(self, result: Dict, output_name: str) -> str:
        """
        전사 결과를 SRT 자막 파일로 저장합니다.
        
        Args:
            result (Dict): Whisper 전사 결과
            output_name (str): 출력 파일명
            
        Returns:
            str: 저장된 SRT 파일 경로
        """
        srt_path = os.path.join(self.subtitle_dir, f"{output_name}.srt")
        
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result["segments"], 1):
                start = segment["start"]
                end = segment["end"]
                text = segment["text"].strip()
                
                # SRT 형식으로 저장
                f.write(f"{i}\n")
                f.write(f"{self._format_timestamp(start)} --> {self._format_timestamp(end)}\n")
                f.write(f"{text}\n\n")
        
        logger.info(f"💾 SRT 자막 저장: {srt_path}")
        return srt_path
    
    def _save_json_result(self, result: Dict, output_name: str) -> str:
        """
        전사 결과를 JSON 파일로 저장합니다.
        
        Args:
            result (Dict): Whisper 전사 결과
            output_name (str): 출력 파일명
            
        Returns:
            str: 저장된 JSON 파일 경로
        """
        json_path = os.path.join(self.subtitle_dir, f"{output_name}.json")
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 JSON 결과 저장: {json_path}")
        return json_path
    
    def _format_timestamp(self, seconds: float) -> str:
        """
        초를 SRT 타임스탬프 형식으로 변환합니다.
        
        Args:
            seconds (float): 초 단위 시간
            
        Returns:
            str: SRT 타임스탬프 (HH:MM:SS,mmm)
        """
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"
    
    def get_subtitle_segments(self, json_path: str) -> List[Dict]:
        """
        JSON 자막 파일에서 세그먼트 정보를 추출합니다.
        
        Args:
            json_path (str): JSON 파일 경로
            
        Returns:
            List[Dict]: 세그먼트 리스트
        """
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("segments", [])
        except Exception as e:
            logger.error(f"자막 세그먼트 로드 실패: {str(e)}")
            return []
    
    def cleanup_old_files(self, days: int = 7) -> Dict:
        """
        오래된 오디오/자막 파일을 정리합니다.
        
        Args:
            days (int): 보관할 일수
            
        Returns:
            Dict: 정리 결과
        """
        import time
        from datetime import datetime, timedelta
        
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        deleted_files = {"audio": [], "subtitles": []}
        
        # 오디오 파일 정리
        for filename in os.listdir(self.audio_dir):
            file_path = os.path.join(self.audio_dir, filename)
            if os.path.getmtime(file_path) < cutoff_time:
                try:
                    os.remove(file_path)
                    deleted_files["audio"].append(filename)
                except:
                    pass
        
        # 자막 파일 정리
        for filename in os.listdir(self.subtitle_dir):
            file_path = os.path.join(self.subtitle_dir, filename)
            if os.path.getmtime(file_path) < cutoff_time:
                try:
                    os.remove(file_path)
                    deleted_files["subtitles"].append(filename)
                except:
                    pass
        
        result = {
            "deleted_audio": len(deleted_files["audio"]),
            "deleted_subtitles": len(deleted_files["subtitles"]),
            "files": deleted_files
        }
        
        logger.info(f"🧹 파일 정리 완료: 오디오 {result['deleted_audio']}개, 자막 {result['deleted_subtitles']}개 삭제")
        return result

if __name__ == "__main__":
    # 테스트 코드
    service = WhisperService()
    
    test_url = input("🎥 테스트할 유튜브 URL 입력: ").strip()
    
    if test_url:
        print("🎵 음성 전사 테스트 시작...")
        result = service.transcribe_youtube_url(test_url, "test_video")
        
        if result.get("success"):
            print(f"✅ 전사 완료!")
            print(f"   - 언어: {result['detected_language']}")
            print(f"   - 세그먼트: {result['total_segments']}개")
            print(f"   - 길이: {result['duration']:.1f}초")
            print(f"   - SRT: {result['srt_file']}")
        else:
            print(f"❌ 전사 실패: {result.get('error')}")
    else:
        print("⚠️ URL이 입력되지 않았습니다.")
