-- FastAPI 프로젝트 테이블 생성 스크립트
-- models.py를 기반으로 작성

-- 1. Users 테이블
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR,
    google_id VARCHAR UNIQUE,
    full_name VARCHAR,
    profile_picture VARCHAR,
    is_active BOOLEAN DEFAULT true,
    login_type VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_users_id ON users (id);
CREATE INDEX ix_users_email ON users (email);
CREATE INDEX ix_users_google_id ON users (google_id);

-- 2. Actors 테이블
CREATE TABLE actors (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL
);

CREATE INDEX ix_actors_id ON actors (id);
CREATE INDEX ix_actors_name ON actors (name);

-- 3. URLs 테이블
CREATE TABLE urls (
    youtube_url TEXT PRIMARY KEY,
    actor_id INTEGER NOT NULL,
    FOREIGN KEY (actor_id) REFERENCES actors (id) ON DELETE CASCADE
);

CREATE INDEX ix_urls_actor_id ON urls (actor_id);

-- 4. Tokens 테이블
CREATE TABLE tokens (
    id SERIAL PRIMARY KEY,
    token_name VARCHAR NOT NULL,
    actor_name VARCHAR NOT NULL,
    category VARCHAR,
    start_time FLOAT NOT NULL,
    end_time FLOAT NOT NULL,
    s3_textgrid_url TEXT,
    s3_pitch_url TEXT,
    s3_bgvoice_url TEXT,
    youtube_url TEXT NOT NULL,
    view_count INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (youtube_url) REFERENCES urls (youtube_url) ON DELETE CASCADE
);

CREATE INDEX ix_tokens_id ON tokens (id);
CREATE INDEX ix_tokens_youtube_url ON tokens (youtube_url);
CREATE INDEX ix_tokens_view_count ON tokens (view_count);

-- 5. Scripts 테이블
CREATE TABLE scripts (
    id SERIAL PRIMARY KEY,
    token_id INTEGER NOT NULL,
    start_time FLOAT NOT NULL,
    end_time FLOAT NOT NULL,
    script TEXT NOT NULL,
    translation TEXT,
    FOREIGN KEY (token_id) REFERENCES tokens (id) ON DELETE CASCADE
);

CREATE INDEX ix_scripts_id ON scripts (id);
CREATE INDEX ix_scripts_token_id ON scripts (token_id);

-- 6. Words 테이블
CREATE TABLE words (
    id SERIAL PRIMARY KEY,
    script_id INTEGER NOT NULL,
    word VARCHAR NOT NULL,
    start_time FLOAT NOT NULL,
    end_time FLOAT NOT NULL,
    FOREIGN KEY (script_id) REFERENCES scripts (id) ON DELETE CASCADE
);

CREATE INDEX ix_words_id ON words (id);
CREATE INDEX ix_words_script_id ON words (script_id);

-- 7. Actor Aliases 테이블
CREATE TABLE actor_aliases (
    id SERIAL PRIMARY KEY,
    actor_id INTEGER NOT NULL,
    name VARCHAR NOT NULL,
    FOREIGN KEY (actor_id) REFERENCES actors (id) ON DELETE CASCADE,
    UNIQUE (actor_id, name)
);

CREATE INDEX ix_actor_aliases_actor_id ON actor_aliases (actor_id);
CREATE INDEX ix_actor_aliases_name ON actor_aliases (name);

-- 8. Token Actors 테이블
CREATE TABLE token_actors (
    id SERIAL PRIMARY KEY,
    token_id INTEGER NOT NULL,
    actor_id INTEGER NOT NULL,
    FOREIGN KEY (token_id) REFERENCES tokens (id) ON DELETE CASCADE,
    FOREIGN KEY (actor_id) REFERENCES actors (id) ON DELETE CASCADE
);

CREATE INDEX ix_token_actors_id ON token_actors (id);
CREATE INDEX ix_token_actors_token_id ON token_actors (token_id);
CREATE INDEX ix_token_actors_actor_id ON token_actors (actor_id);

-- 9. Bookmarks 테이블
CREATE TABLE bookmarks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (token_id) REFERENCES tokens (id) ON DELETE CASCADE,
    UNIQUE (user_id, token_id)
);

CREATE INDEX ix_bookmarks_id ON bookmarks (id);
CREATE INDEX ix_bookmarks_user_id ON bookmarks (user_id);
CREATE INDEX ix_bookmarks_token_id ON bookmarks (token_id);

-- 10. Analysis Results 테이블
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    token_id INTEGER NOT NULL,
    analysis_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (token_id) REFERENCES tokens (id) ON DELETE CASCADE
);

CREATE INDEX ix_analysis_results_id ON analysis_results (id);
CREATE INDEX ix_analysis_results_token_id ON analysis_results (token_id);

-- 완료 메시지
SELECT 'All tables created successfully!' as status;
