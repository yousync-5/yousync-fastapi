"""
배우 이미지 크롤링 및 얼굴 인코딩 서비스

Google Images에서 배우 이미지를 크롤링하고 얼굴 인코딩을 생성합니다.
"""

import os
import face_recognition
import numpy as np
from icrawler.builtin import GoogleImageCrawler
from typing import List, Optional
import logging
import shutil

logger = logging.getLogger(__name__)

class CrawlService:
    def __init__(self, base_dir: str = "storage"):
        """
        크롤링 서비스 초기화
        
        Args:
            base_dir (str): 기본 저장 디렉토리
        """
        self.base_dir = base_dir
        self.image_root = os.path.join(base_dir, "actor_images")
        self.encoding_root = os.path.join(base_dir, "actor_encodings")
        
        # 디렉토리 생성
        os.makedirs(self.image_root, exist_ok=True)
        os.makedirs(self.encoding_root, exist_ok=True)
    
    def download_actor_images(self, actor_name: str, max_images: int = 50) -> bool:
        """
        Google Images에서 배우 이미지를 크롤링합니다.
        
        Args:
            actor_name (str): 배우 이름
            max_images (int): 최대 다운로드 이미지 수
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 안전한 파일명 생성
            actor_key = self._sanitize_filename(actor_name)
            save_dir = os.path.join(self.image_root, actor_key)
            
            # 기존 디렉토리가 있으면 삭제 후 재생성
            if os.path.exists(save_dir):
                shutil.rmtree(save_dir)
            os.makedirs(save_dir, exist_ok=True)
            
            logger.info(f"📥 배우 이미지 크롤링 시작: {actor_name}")
            
            # Google Images 크롤러 설정
            crawler = GoogleImageCrawler(
                storage={"root_dir": save_dir},
                downloader_cls=None,  # 기본 다운로더 사용
            )
            
            # 검색 키워드: 배우명 + face (얼굴 이미지 우선)
            search_keyword = f"{actor_name} face actor"
            crawler.crawl(keyword=search_keyword, max_num=max_images)
            
            # 다운로드된 이미지 수 확인
            downloaded_count = len([f for f in os.listdir(save_dir) 
                                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))])
            
            logger.info(f"✅ {actor_name}: {downloaded_count}개 이미지 다운로드 완료")
            return downloaded_count > 0
            
        except Exception as e:
            logger.error(f"❌ {actor_name} 이미지 크롤링 실패: {str(e)}")
            return False
    
    def encode_and_save_actor(self, actor_name: str, min_faces: int = 3) -> bool:
        """
        배우 이미지들에서 얼굴을 인코딩하고 평균 인코딩을 저장합니다.
        
        Args:
            actor_name (str): 배우 이름
            min_faces (int): 최소 필요한 얼굴 수
            
        Returns:
            bool: 성공 여부
        """
        try:
            actor_key = self._sanitize_filename(actor_name)
            folder_path = os.path.join(self.image_root, actor_key)
            
            if not os.path.exists(folder_path):
                logger.error(f"❌ {actor_name} 이미지 폴더가 존재하지 않습니다")
                return False
            
            encodings = []
            processed_count = 0
            
            logger.info(f"🔍 {actor_name} 얼굴 인코딩 시작...")
            
            # 모든 이미지 파일 처리
            for filename in os.listdir(folder_path):
                if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    continue
                
                img_path = os.path.join(folder_path, filename)
                processed_count += 1
                
                try:
                    # 이미지 로드 및 얼굴 인코딩
                    image = face_recognition.load_image_file(img_path)
                    faces = face_recognition.face_encodings(image)
                    
                    if faces:
                        encodings.append(faces[0])  # 첫 번째 얼굴만 사용
                        logger.debug(f"✅ 인코딩 성공: {filename}")
                    else:
                        logger.debug(f"⚠️ 얼굴 없음: {filename}")
                        
                except Exception as e:
                    logger.debug(f"⚠️ 인코딩 실패 {filename}: {str(e)}")
                
                # 이미지 삭제로 용량 절약
                try:
                    os.remove(img_path)
                except:
                    pass
            
            # 최소 얼굴 수 확인
            if len(encodings) < min_faces:
                logger.warning(f"⚠️ {actor_name}: 얼굴 {len(encodings)}개 (최소 {min_faces}개 필요)")
                return False
            
            # 평균 인코딩 계산 및 저장
            avg_encoding = np.mean(encodings, axis=0)
            encoding_path = os.path.join(self.encoding_root, f"{actor_key}.npy")
            np.save(encoding_path, avg_encoding)
            
            logger.info(f"💾 {actor_name} 인코딩 저장 완료: {len(encodings)}개 얼굴 평균")
            
            # 임시 이미지 폴더 삭제
            try:
                shutil.rmtree(folder_path)
            except:
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"❌ {actor_name} 인코딩 실패: {str(e)}")
            return False
    
    def process_actor_list(self, actors: List[str], max_images_per_actor: int = 50) -> dict:
        """
        배우 리스트를 일괄 처리합니다.
        
        Args:
            actors (List[str]): 배우 이름 리스트
            max_images_per_actor (int): 배우당 최대 이미지 수
            
        Returns:
            dict: 처리 결과 (성공/실패 배우 목록)
        """
        results = {
            "success": [],
            "failed": [],
            "total": len(actors)
        }
        
        logger.info(f"🎭 {len(actors)}명 배우 처리 시작...")
        
        for i, actor in enumerate(actors, 1):
            logger.info(f"📍 진행률: {i}/{len(actors)} - {actor}")
            
            try:
                # 1. 이미지 크롤링
                if not self.download_actor_images(actor, max_images_per_actor):
                    results["failed"].append({"actor": actor, "reason": "크롤링 실패"})
                    continue
                
                # 2. 얼굴 인코딩
                if not self.encode_and_save_actor(actor):
                    results["failed"].append({"actor": actor, "reason": "인코딩 실패"})
                    continue
                
                results["success"].append(actor)
                logger.info(f"✅ {actor} 처리 완료")
                
            except Exception as e:
                logger.error(f"❌ {actor} 처리 중 오류: {str(e)}")
                results["failed"].append({"actor": actor, "reason": str(e)})
        
        logger.info(f"🎯 처리 완료: 성공 {len(results['success'])}명, 실패 {len(results['failed'])}명")
        return results
    
    def get_available_actors(self) -> List[str]:
        """
        저장된 배우 인코딩 목록을 반환합니다.
        
        Returns:
            List[str]: 사용 가능한 배우 이름 리스트
        """
        try:
            actors = []
            for filename in os.listdir(self.encoding_root):
                if filename.endswith('.npy'):
                    actor_name = filename.replace('.npy', '')
                    actors.append(actor_name)
            return sorted(actors)
        except:
            return []
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        파일명에 사용할 수 없는 문자를 제거합니다.
        
        Args:
            filename (str): 원본 파일명
            
        Returns:
            str: 안전한 파일명
        """
        # 공백을 언더스코어로, 특수문자 제거
        safe_name = filename.replace(' ', '_')
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c in ['_', '-'])
        return safe_name

if __name__ == "__main__":
    # 테스트 코드
    service = CrawlService()
    
    test_actors = ["김민수", "박서준", "아이유"]
    
    for actor in test_actors:
        print(f"\n=== {actor} 처리 시작 ===")
        
        # 이미지 크롤링
        if service.download_actor_images(actor, max_images=10):
            # 얼굴 인코딩
            if service.encode_and_save_actor(actor):
                print(f"✅ {actor} 완료")
            else:
                print(f"❌ {actor} 인코딩 실패")
        else:
            print(f"❌ {actor} 크롤링 실패")
    
    # 저장된 배우 목록 확인
    available_actors = service.get_available_actors()
    print(f"\n📋 저장된 배우: {available_actors}")
