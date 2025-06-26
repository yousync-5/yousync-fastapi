-- 초기 데이터베이스 설정 스크립트
-- Docker 컨테이너 시작시 자동으로 실행됩니다

-- 데이터베이스가 존재하지 않으면 생성 (이미 docker-compose.yml에서 설정함)
-- CREATE DATABASE IF NOT EXISTS movie_script_db;

-- 필요한 확장 프로그램 설치 (예: UUID 생성용)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 초기 테이블 생성은 FastAPI 앱에서 자동으로 처리되므로 여기서는 생략
-- (SQLAlchemy의 Base.metadata.create_all()이 처리함)

-- 로그 출력
SELECT 'Database initialization completed!' as status;
