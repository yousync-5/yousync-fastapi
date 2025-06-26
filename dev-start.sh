#!/bin/bash

# 개발 환경 시작 스크립트
echo "🚀 FastAPI 개발 환경을 시작합니다..."

# Docker Compose로 모든 서비스 시작
docker-compose up -d

echo "✅ 서비스 시작 완료!"
echo ""
echo "📝 접속 정보:"
echo "  - API 서버: http://localhost:8000"
echo "  - API 문서: http://localhost:8000/docs"
echo "  - pgAdmin:  http://localhost:5050"
echo ""
echo "🛑 종료하려면: ./dev-stop.sh 또는 docker-compose down"
