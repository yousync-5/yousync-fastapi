"""
얼굴 매칭 서비스

이미지 프레임에서 얼굴을 인식하고 저장된 배우 인코딩과 비교하여 매칭합니다.
"""

import os
import numpy as np
import face_recognition
from typing import List, Tuple, Optional, Dict
import logging
from PIL import Image
import io
import base64

logger = logging.getLogger(__name__)

class FaceService:
    def __init__(self, base_dir: str = "storage"):
        """
        얼굴 매칭 서비스 초기화
        
        Args:
            base_dir (str): 기본 저장 디렉토리
        """
        self.base_dir = base_dir
        self.encoding_root = os.path.join(base_dir, "actor_encodings")
        self.frame_root = os.path.join(base_dir, "scene_frames")
        
        # 디렉토리 생성
        os.makedirs(self.encoding_root, exist_ok=True)
        os.makedirs(self.frame_root, exist_ok=True)
        
        # 배우 인코딩 캐시
        self._actor_encodings = {}
        self._load_actor_encodings()
    
    def _load_actor_encodings(self) -> None:
        """저장된 배우 인코딩들을 메모리에 로드합니다."""
        try:
            self._actor_encodings = {}
            
            if not os.path.exists(self.encoding_root):
                logger.warning("배우 인코딩 디렉토리가 존재하지 않습니다")
                return
            
            for filename in os.listdir(self.encoding_root):
                if not filename.endswith(".npy"):
                    continue
                
                actor_name = filename.replace(".npy", "")
                encoding_path = os.path.join(self.encoding_root, filename)
                
                try:
                    encoding = np.load(encoding_path)
                    self._actor_encodings[actor_name] = encoding
                    logger.debug(f"✅ {actor_name} 인코딩 로드")
                except Exception as e:
                    logger.error(f"❌ {actor_name} 인코딩 로드 실패: {str(e)}")
            
            logger.info(f"📋 총 {len(self._actor_encodings)}명 배우 인코딩 로드 완료")
            
        except Exception as e:
            logger.error(f"배우 인코딩 로드 중 오류: {str(e)}")
            self._actor_encodings = {}
    
    def match_face_from_file(self, image_path: str, threshold: float = 0.6) -> Dict:
        """
        이미지 파일에서 얼굴을 인식하고 배우와 매칭합니다.
        
        Args:
            image_path (str): 이미지 파일 경로
            threshold (float): 매칭 임계값 (낮을수록 엄격)
            
        Returns:
            Dict: 매칭 결과
        """
        try:
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "error": "이미지 파일이 존재하지 않습니다"
                }
            
            # 이미지에서 얼굴 인코딩 추출
            frame_image = face_recognition.load_image_file(image_path)
            frame_encodings = face_recognition.face_encodings(frame_image)
            
            if not frame_encodings:
                return {
                    "success": False,
                    "error": "이미지에서 얼굴을 찾을 수 없습니다"
                }
            
            # 첫 번째 얼굴 사용
            frame_encoding = frame_encodings[0]
            
            return self._match_encoding(frame_encoding, threshold)
            
        except Exception as e:
            logger.error(f"파일 얼굴 매칭 실패: {str(e)}")
            return {
                "success": False,
                "error": f"얼굴 매칭 중 오류가 발생했습니다: {str(e)}"
            }
    
    def match_face_from_base64(self, base64_image: str, threshold: float = 0.6) -> Dict:
        """
        Base64 인코딩된 이미지에서 얼굴을 인식하고 배우와 매칭합니다.
        
        Args:
            base64_image (str): Base64 인코딩된 이미지
            threshold (float): 매칭 임계값
            
        Returns:
            Dict: 매칭 결과
        """
        try:
            # Base64 디코딩
            image_data = base64.b64decode(base64_image)
            image = Image.open(io.BytesIO(image_data))
            
            # PIL Image를 numpy array로 변환
            image_array = np.array(image)
            
            # 얼굴 인코딩 추출
            frame_encodings = face_recognition.face_encodings(image_array)
            
            if not frame_encodings:
                return {
                    "success": False,
                    "error": "이미지에서 얼굴을 찾을 수 없습니다"
                }
            
            # 첫 번째 얼굴 사용
            frame_encoding = frame_encodings[0]
            
            return self._match_encoding(frame_encoding, threshold)
            
        except Exception as e:
            logger.error(f"Base64 얼굴 매칭 실패: {str(e)}")
            return {
                "success": False,
                "error": f"얼굴 매칭 중 오류가 발생했습니다: {str(e)}"
            }
    
    def _match_encoding(self, frame_encoding: np.ndarray, threshold: float = 0.6) -> Dict:
        """
        얼굴 인코딩을 배우 인코딩들과 비교하여 매칭합니다.
        
        Args:
            frame_encoding (np.ndarray): 매칭할 얼굴 인코딩
            threshold (float): 매칭 임계값
            
        Returns:
            Dict: 매칭 결과
        """
        try:
            if not self._actor_encodings:
                return {
                    "success": False,
                    "error": "저장된 배우 인코딩이 없습니다"
                }
            
            min_distance = float("inf")
            best_match = "unknown"
            all_distances = {}
            
            # 모든 배우 인코딩과 거리 계산
            for actor_name, actor_encoding in self._actor_encodings.items():
                try:
                    distance = face_recognition.face_distance([actor_encoding], frame_encoding)[0]
                    all_distances[actor_name] = float(distance)
                    
                    logger.debug(f"{actor_name} 거리: {distance:.4f}")
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_match = actor_name
                        
                except Exception as e:
                    logger.error(f"{actor_name} 거리 계산 실패: {str(e)}")
                    continue
            
            # 임계값 검사
            if min_distance > threshold:
                best_match = "unknown"
                confidence = 0.0
            else:
                # 신뢰도 계산 (거리를 백분율로 변환)
                confidence = max(0, (1 - min_distance) * 100)
            
            result = {
                "success": True,
                "matched_actor": best_match,
                "confidence": round(confidence, 2),
                "distance": round(min_distance, 4),
                "threshold_used": threshold,
                "all_distances": {k: round(v, 4) for k, v in all_distances.items()},
                "total_actors_compared": len(all_distances)
            }
            
            logger.info(f"🎯 매칭 결과: {best_match} (신뢰도: {confidence:.1f}%, 거리: {min_distance:.4f})")
            
            return result
            
        except Exception as e:
            logger.error(f"인코딩 매칭 실패: {str(e)}")
            return {
                "success": False,
                "error": f"얼굴 매칭 중 오류가 발생했습니다: {str(e)}"
            }
    
    def batch_match_frames(self, frame_paths: List[str], threshold: float = 0.6) -> List[Dict]:
        """
        여러 이미지 프레임을 일괄 매칭합니다.
        
        Args:
            frame_paths (List[str]): 이미지 파일 경로 리스트
            threshold (float): 매칭 임계값
            
        Returns:
            List[Dict]: 각 이미지의 매칭 결과 리스트
        """
        results = []
        
        logger.info(f"🔍 {len(frame_paths)}개 프레임 일괄 매칭 시작...")
        
        for i, frame_path in enumerate(frame_paths, 1):
            logger.info(f"📍 진행률: {i}/{len(frame_paths)} - {os.path.basename(frame_path)}")
            
            result = self.match_face_from_file(frame_path, threshold)
            result["frame_path"] = frame_path
            result["frame_index"] = i - 1
            
            results.append(result)
        
        # 통계 정보
        successful_matches = sum(1 for r in results if r.get("success") and r.get("matched_actor") != "unknown")
        
        logger.info(f"🎯 일괄 매칭 완료: {successful_matches}/{len(frame_paths)}개 성공")
        
        return results
    
    def get_available_actors(self) -> List[str]:
        """
        매칭 가능한 배우 목록을 반환합니다.
        
        Returns:
            List[str]: 배우 이름 리스트
        """
        return list(self._actor_encodings.keys())
    
    def reload_encodings(self) -> int:
        """
        배우 인코딩을 다시 로드합니다.
        
        Returns:
            int: 로드된 배우 수
        """
        self._load_actor_encodings()
        return len(self._actor_encodings)
    
    def get_statistics(self) -> Dict:
        """
        얼굴 매칭 서비스 통계를 반환합니다.
        
        Returns:
            Dict: 통계 정보
        """
        return {
            "total_actors": len(self._actor_encodings),
            "available_actors": list(self._actor_encodings.keys()),
            "encoding_directory": self.encoding_root,
            "frame_directory": self.frame_root
        }

if __name__ == "__main__":
    # 테스트 코드
    service = FaceService()
    
    # 통계 정보 출력
    stats = service.get_statistics()
    print(f"📊 매칭 서비스 통계:")
    print(f"   - 총 배우 수: {stats['total_actors']}")
    print(f"   - 배우 목록: {stats['available_actors']}")
    
    # 테스트 이미지가 있다면 매칭 테스트
    test_image_path = "storage/scene_frames/test_frame.jpg"
    if os.path.exists(test_image_path):
        result = service.match_face_from_file(test_image_path)
        print(f"\n🎯 테스트 매칭 결과:")
        print(f"   - 매칭 배우: {result.get('matched_actor', 'N/A')}")
        print(f"   - 신뢰도: {result.get('confidence', 0)}%")
    else:
        print(f"\n⚠️ 테스트 이미지가 없습니다: {test_image_path}")
