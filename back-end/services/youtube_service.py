# """
# YouTube 메타데이터 추출 서비스

# 유튜브 URL에서 제목, 태그, 설명 등의 메타데이터를 추출합니다.
# """

# import yt_dlp
# from typing import Dict, Optional
# import logging

# logger = logging.getLogger(__name__)

# class YouTubeService:
#     @staticmethod
#     def extract_metadata(url: str) -> Dict[str, any]:
#         """
#         유튜브 URL에서 메타데이터를 추출합니다.
        
#         Args:
#             url (str): 유튜브 비디오 URL
            
#         Returns:
#             Dict: 메타데이터 딕셔너리 (title, tags, description 포함)
            
#         Raises:
#             Exception: 메타데이터 추출 실패 시
#         """
#         try:
#             ydl_opts = {
#                 'quiet': True,  # 출력 최소화
#                 'no_warnings': True
#             }
            
#             with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#                 info = ydl.extract_info(url, download=False)
                
#                 metadata = {
#                     'title': info.get('title', ''),
#                     'tags': info.get('tags', []),
#                     'description': info.get('description', ''),
#                     'duration': info.get('duration', 0),
#                     'upload_date': info.get('upload_date', ''),
#                     'uploader': info.get('uploader', ''),
#                     'view_count': info.get('view_count', 0),
#                     'video_id': info.get('id', '')
#                 }
                
#                 logger.info(f"메타데이터 추출 성공: {metadata['title']}")
#                 return metadata
                
#         except Exception as e:
#             logger.error(f"메타데이터 추출 실패: {str(e)}")
#             raise Exception(f"유튜브 메타데이터 추출 중 오류가 발생했습니다: {str(e)}")
    
#     @staticmethod
#     def validate_youtube_url(url: str) -> bool:
#         """
#         유튜브 URL이 유효한지 검증합니다.
        
#         Args:
#             url (str): 검증할 URL
            
#         Returns:
#             bool: 유효한 유튜브 URL인지 여부
#         """
#         youtube_domains = [
#             'youtube.com',
#             'youtu.be',
#             'www.youtube.com',
#             'm.youtube.com'
#         ]
        
#         return any(domain in url for domain in youtube_domains)

# if __name__ == "__main__":
#     # 테스트 코드
#     service = YouTubeService()
#     test_url = 'https://www.youtube.com/watch?v=fFSJiqNdbgU'
    
#     try:
#         metadata = service.extract_metadata(test_url)
#         print('제목:', metadata['title'])
#         print('태그:', metadata['tags'])
#         print('설명:', metadata['description'][:100] + '...' if len(metadata['description']) > 100 else metadata['description'])
#     except Exception as e:
#         print(f"오류: {e}")
