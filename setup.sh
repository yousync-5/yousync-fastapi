#!/bin/bash

echo "🎬 FastAPI 영화/스크립트 관리 시스템 설정 스크립트"
echo "=================================================="

# .env 파일 존재 확인
if [ ! -f ".env" ]; then
    echo "📁 .env 파일이 없습니다. .env.example에서 복사합니다..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env 파일이 생성되었습니다."
    else
        echo "❌ .env.example 파일을 찾을 수 없습니다."
        exit 1
    fi
else
    echo "✅ .env 파일이 이미 존재합니다."
fi

# Docker 설치 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않았습니다. https://www.docker.com/get-started 에서 설치하세요."
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker가 실행되지 않았습니다. Docker Desktop을 시작하세요."
    exit 1
fi

echo "✅ Docker가 정상적으로 실행 중입니다."

# Docker Compose 실행
echo "🚀 Docker 컨테이너를 시작합니다..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 설정 완료!"
    echo ""
    echo "📝 접속 정보:"
    echo "  - API 서버: http://localhost:8000"
    echo "  - API 문서: http://localhost:8000/docs"
    echo "  - pgAdmin:  http://localhost:5050"
    echo "    * 이메일: admin@example.com"
    echo "    * 비밀번호: admin123"
    echo ""
    echo "🛑 종료: docker-compose down"
    echo "📊 상태확인: docker-compose ps"
    echo "📋 로그보기: docker-compose logs -f"
else
    echo "❌ 컨테이너 시작에 실패했습니다. 로그를 확인하세요:"
    echo "   docker-compose logs"
fi
