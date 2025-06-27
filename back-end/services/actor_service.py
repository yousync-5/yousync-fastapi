"""
영화 배우 정보 추출 서비스

TMDb API를 사용하여 영화 제목으로부터 출연 배우 목록을 가져옵니다.
"""

import os
from tmdbv3api import TMDb, Movie
from typing import List, Tuple, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ActorService:
    def __init__(self):
        """TMDb API 클라이언트 초기화"""
        self.tmdb = TMDb()
        # 환경변수에서 API 키를 가져오거나 기본값 사용 (보안상 환경변수 권장)
        self.tmdb.api_key = os.getenv("TMDB_API_KEY", "5085b3026fc2e7cd7fdba3b0f828018e")
        self.tmdb.language = "ko-KR"  # 한국어 우선, 없으면 영어
        self.movie = Movie()
    
    def get_cast_list_by_title(self, title: str) -> Tuple[List[str], str]:
        """
        영화 제목으로 출연 배우 목록을 가져옵니다.
        
        Args:
            title (str): 영화 제목
            
        Returns:
            Tuple[List[str], str]: (배우 목록, 매칭된 영화 제목)
        """
        try:
            logger.info(f"🎬 영화 검색 시작: {title}")
            
            # TMDb에서 영화 검색
            search_results = self.movie.search(title)
            
            if not search_results:
                logger.warning(f"검색 결과 없음: {title}")
                return [], "unknown"
            
            # 첫 번째 결과 사용 (가장 관련도가 높음)
            movie_result = search_results[0]
            movie_id = movie_result.id
            
            # 상세 정보 및 출연진 정보 가져오기
            details = self.movie.details(movie_id, append_to_response="credits")
            
            # 다큐멘터리나 인터뷰 필터링
            if self._is_excluded_genre(details):
                logger.warning(f"제외된 장르: {details.title}")
                return [], "excluded_genre"
            
            # 출연진 정보 추출
            cast_list = details.credits.get('cast', [])
            cast_names = [actor.name for actor in cast_list[:20]]  # 상위 20명만
            
            matched_title = details.title
            
            logger.info(f"🎯 매칭된 영화: {matched_title}")
            logger.info(f"👥 출연 배우 ({len(cast_names)}명): {cast_names}")
            
            return cast_names, matched_title
            
        except Exception as e:
            logger.error(f"배우 정보 추출 실패: {str(e)}")
            return [], "error"
    
    def get_cast_list_from_metadata(self, metadata: Dict) -> Tuple[List[str], str]:
        """
        유튜브 메타데이터에서 영화를 찾고 출연 배우 목록을 가져옵니다.
        
        Args:
            metadata (Dict): 유튜브 메타데이터 (title, tags, description 포함)
            
        Returns:
            Tuple[List[str], str]: (배우 목록, 매칭된 영화 제목)
        """
        title = metadata.get('title', '')
        tags = metadata.get('tags', [])
        description = metadata.get('description', '')
        
        logger.info(f"🎬 유튜브 영상 제목: {title}")
        
        # 검색 후보들 (우선순위: 제목 > 설명 > 태그)
        candidates = [title, description] + tags
        
        for query in candidates:
            if not query or not isinstance(query, str) or len(query.strip()) < 2:
                continue
                
            try:
                search_results = self.movie.search(query)
                if not search_results:
                    continue
                
                for result in search_results:
                    try:
                        details = self.movie.details(result.id, append_to_response="credits")
                        
                        # 필터링 검사
                        if self._is_excluded_genre(details) or self._is_actor_profile(details):
                            continue
                        
                        # 성공적으로 찾았음
                        cast_list = details.credits.get('cast', [])
                        cast_names = [actor.name for actor in cast_list[:20]]
                        matched_title = details.title
                        
                        logger.info(f"🎯 TMDb 검색된 제목: {matched_title}")
                        logger.info(f"👥 출연 배우 ({len(cast_names)}명): {cast_names}")
                        
                        return cast_names, matched_title
                        
                    except Exception:
                        continue
                        
            except Exception:
                continue
        
        logger.warning("❌ TMDb에서 영화 검색 실패")
        return [], "unknown"
    
    def _is_excluded_genre(self, details) -> bool:
        """다큐멘터리나 인터뷰 장르인지 확인"""
        try:
            genre_names = [g['name'].lower() for g in details.genres]
            excluded_genres = ['documentary', 'talk', '다큐멘터리', '토크쇼']
            
            if any(genre in genre_names for genre in excluded_genres):
                logger.info(f"⚠️ '{details.title}'은 제외 장르로 판단됨")
                return True
        except:
            pass
        return False
    
    def _is_actor_profile(self, details) -> bool:
        """배우 프로필이나 전기물인지 확인"""
        try:
            overview = getattr(details, "overview", "").lower()
            title_text = getattr(details, "title", "").lower()
            
            profile_keywords = ["actor", "profile", "biography", "배우", "프로필", "전기"]
            
            if any(keyword in overview for keyword in profile_keywords) or \
               any(keyword in title_text for keyword in profile_keywords):
                logger.info(f"⚠️ '{details.title}'은 배우 프로필/전기물로 판단됨")
                return True
        except:
            pass
        return False

if __name__ == "__main__":
    # 테스트 코드
    service = ActorService()
    
    # 직접 제목으로 테스트
    cast, title = service.get_cast_list_by_title("조커")
    print(f"\n🎯 테스트 완료 - 영화: {title}")
    print(f"👥 배우 목록: {cast}")
    
    # 메타데이터로 테스트
    sample_metadata = {
        "title": "Joker",
        "tags": ['joker 2019', 'joaquin phoenix', 'dc comics'],
        "description": "Joker (2019) Scene: Can you introduce me as Joker?"
    }
    
    cast, title = service.get_cast_list_from_metadata(sample_metadata)
    print(f"\n🎯 메타데이터 테스트 완료 - 영화: {title}")
    print(f"👥 배우 목록: {cast}")
