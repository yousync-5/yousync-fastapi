-- 데이터베이스 초기화 스크립트
-- 이 스크립트는 PostgreSQL 컨테이너가 처음 시작될 때 실행됩니다

-- admin 사용자 생성 (이미 존재하지 않는 경우에만)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'admin') THEN
        CREATE USER admin WITH PASSWORD 'securepassword123';
    END IF;
END
$$;

-- 필요한 확장 설치
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- admin 사용자에게 데이터베이스 권한 부여
GRANT ALL PRIVILEGES ON DATABASE movie_script_db TO admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;

-- 예: 기본 관리자 계정 생성
-- INSERT INTO users (email, password_hash, is_active, is_admin) 
-- VALUES ('admin@example.com', 'hashed_password_here', true, true);
