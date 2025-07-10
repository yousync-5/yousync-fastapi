# 기존 테이블의 배우이름을 바탕으로  actor_aliases(배우 별칭을 생성한다.)
# EN_KO_DICT에 정의해야 함
# back-end/tmp/backfill_aliases.py
"""
배우(Actor) 레코드를 훑어보면서
  1) 원본 이름(영/한)을 alias 로 넣고
  2) 영문 ↔ 한글 대응 이름을 자동 생성하여 alias 로 추가한다.

중복(UNIQUE(actor_id, name))은 merge() 덕분에 무시됨.
실행:  python back-end/scripts/backfill_aliases.py
"""

import re
from sqlalchemy.orm import Session
from pathlib import Path
import sys

# ── 프로젝트 경로 세팅 ──────────────────────────
BASE_DIR = Path(__file__).resolve().parents[1]   # back-end/
sys.path.append(str(BASE_DIR))

from database import engine
from models import Actor, ActorAlias

# ── (선택) hangul-romanize 로마자 라이브러리 ───
try:
    from hangul_romanize import Transliter
    from hangul_romanize.rule import academic
    transliter = Transliter(academic)
except ImportError:
    transliter = None   # 영→한만 지원하거나, pypi 설치 필요

# ── 영문→한글 사전 매핑 (예시) ──────────────────
EN_KO_DICT = {
    "liam nesson":        "리암니슨",
    "timothée chalamet":  "티모시샬라메",
    "brad pitt":          "브래드피트",
    "saoirse ronan":      "시얼샤로넌",
    "russell crowe":      "러셀크로우",
}

def english_to_korean(name_en: str) -> str | None:
    return EN_KO_DICT.get(name_en.lower())

def korean_to_english(name_ko: str) -> str | None:
    if transliter:
        return transliter.translit(name_ko)
    return None

def ensure_aliases(session: Session, actor: Actor) -> None:
    """actor 1명에 대해 alias 레코드들을 보장"""
    names_current = {al.name for al in actor.aliases}

    # 1) 원본 이름
    if actor.name not in names_current:
        session.add(ActorAlias(actor_id=actor.id, name=actor.name))

    # 2) 교차 변환
    if re.search(r"[가-힣]", actor.name):               # 한글 → 영문
        eng = korean_to_english(actor.name)
        if eng and eng not in names_current:
            session.add(ActorAlias(actor_id=actor.id, name=eng))
    else:                                              # 영문 → 한글
        kor = english_to_korean(actor.name)
        if kor and kor not in names_current:
            session.add(ActorAlias(actor_id=actor.id, name=kor))

def main() -> None:
    with Session(engine) as sess:
        actors = sess.query(Actor).all()
        for actor in actors:
            ensure_aliases(sess, actor)
        sess.commit()
        print(f"✅ 별칭 백필 완료! 총 {len(actors)}명의 배우를 처리했습니다.")

if __name__ == "__main__":
    main()