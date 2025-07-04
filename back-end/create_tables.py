#!/usr/bin/env python3
"""
RDS에 테이블을 생성하는 스크립트
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# .env 파일 로드
load_dotenv()

# 데이터베이스 연결
DATABASE_URL = os.getenv('DATABASE_URL')
print(f'DATABASE_URL: {DATABASE_URL}')

try:
    engine = create_engine(DATABASE_URL)
    
    # 연결 테스트
    with engine.connect() as conn:
        result = conn.execute(text('SELECT version()'))
        version = result.fetchone()[0]
        print(f'✅ PostgreSQL 연결 성공!')
        print(f'버전: {version}')
    
    # models.py에서 Base를 가져와서 테이블 생성
    try:
        from models import Base
        Base.metadata.create_all(bind=engine)
        print('✅ 모든 테이블이 성공적으로 생성되었습니다!')
        
        # 생성된 테이블 목록 확인
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            print('\n📋 생성된 테이블 목록:')
            for table in tables:
                print(f'  - {table[0]}')
                
    except Exception as e:
        print(f'❌ 테이블 생성 실패: {e}')
        sys.exit(1)
        
except Exception as e:
    print(f'❌ 데이터베이스 연결 실패: {e}')
    sys.exit(1)
