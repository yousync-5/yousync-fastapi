# 스크립트 관련 API 엔드포인트들을 관리하는 라우터
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# 데이터베이스 관련 임포트
from database import get_db
from models import Script
from schemas import Script as ScriptSchema, ScriptCreate

# APIRouter 인스턴스 생성 - 모든 스크립트 관련 엔드포인트의 접두사로 "/scripts" 사용
router = APIRouter(
    prefix="/scripts",  # 모든 경로 앞에 /scripts가 자동으로 붙음
    tags=["scripts"]    # OpenAPI 문서에서 이 그룹의 태그명
)

# 스크립트 생성 API - POST 요청으로 새로운 스크립트 데이터를 받아 데이터베이스에 저장
@router.post("/", response_model=ScriptSchema)
def create_script(script: ScriptCreate, db: Session = Depends(get_db)):
    """
    새로운 스크립트를 생성합니다.
    
    - **title**: 스크립트 제목 (필수)
    - **content**: 스크립트 내용 (필수)
    - **author**: 작성자 이름 (필수)
    """
    db_script = Script(**script.dict())  # Pydantic 모델을 SQLAlchemy 모델로 변환
    db.add(db_script)  # 데이터베이스 세션에 추가
    db.commit()  # 변경사항 커밋 (실제 DB에 저장)
    db.refresh(db_script)  # 저장된 데이터를 다시 불러와서 ID 등 업데이트
    return db_script

# 모든 스크립트 조회 API - 페이지네이션 지원 (skip: 건너뛸 개수, limit: 가져올 최대 개수)
@router.get("/", response_model=List[ScriptSchema])
def read_scripts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    모든 스크립트 목록을 조회합니다.
    
    - **skip**: 건너뛸 항목 수 (기본값: 0)
    - **limit**: 가져올 최대 항목 수 (기본값: 100)
    """
    scripts = db.query(Script).offset(skip).limit(limit).all()  # SQL: SELECT * FROM scripts LIMIT 100 OFFSET 0
    return scripts

# 특정 스크립트 조회 API - ID로 하나의 스크립트만 가져오기
@router.get("/{script_id}", response_model=ScriptSchema)
def read_script(script_id: int, db: Session = Depends(get_db)):
    """
    특정 ID의 스크립트를 조회합니다.
    
    - **script_id**: 조회할 스크립트의 ID
    """
    script = db.query(Script).filter(Script.id == script_id).first()  # SQL: SELECT * FROM scripts WHERE id = script_id
    if script is None:  # 해당 ID의 스크립트가 없으면 404 에러 반환
        raise HTTPException(status_code=404, detail="Script not found")
    return script

# 스크립트 수정 API - PUT 요청으로 기존 스크립트 데이터를 업데이트
@router.put("/{script_id}", response_model=ScriptSchema)
def update_script(script_id: int, script: ScriptCreate, db: Session = Depends(get_db)):
    """
    기존 스크립트를 수정합니다.
    
    - **script_id**: 수정할 스크립트의 ID
    - **title**: 수정할 스크립트 제목
    - **content**: 수정할 스크립트 내용
    - **author**: 수정할 작성자 이름
    """
    db_script = db.query(Script).filter(Script.id == script_id).first()
    if db_script is None:
        raise HTTPException(status_code=404, detail="Script not found")
    
    # 기존 스크립트 데이터를 새로운 데이터로 업데이트
    for field, value in script.dict().items():
        setattr(db_script, field, value)
    
    db.commit()  # 변경사항 저장
    db.refresh(db_script)  # 업데이트된 데이터 다시 로드
    return db_script

# 스크립트 삭제 API - DELETE 요청으로 특정 스크립트를 삭제
@router.delete("/{script_id}")
def delete_script(script_id: int, db: Session = Depends(get_db)):
    """
    특정 ID의 스크립트를 삭제합니다.
    
    - **script_id**: 삭제할 스크립트의 ID
    """
    db_script = db.query(Script).filter(Script.id == script_id).first()
    if db_script is None:
        raise HTTPException(status_code=404, detail="Script not found")
    
    db.delete(db_script)  # 데이터베이스에서 삭제
    db.commit()  # 변경사항 저장
    return {"detail": "Script deleted successfully"}
