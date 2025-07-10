"""
1) Token → Actor 이름 매핑을 시도해 urls.actor_id 채운다
2) 매핑 안 된 (url, actor_name) 목록을 표로 출력
   └─ 실제 배우 테이블에 없는 이름인지, 철자가 다른지 확인용
"""

from pathlib import Path
import sys
from tabulate import tabulate          # pip install tabulate
from sqlalchemy import select, update
from sqlalchemy.orm import Session

# ── 프로젝트 모듈 경로 세팅 ───────────────────────────
BASE_DIR = Path(__file__).resolve().parents[1]   # back-end/
sys.path.append(str(BASE_DIR))

from models import URL, Token, Actor
from database import engine                    # database.py 의 engine

def main() -> None:
    with Session(engine) as sess:
        # ── 1. URL-배우 매핑 시도 ────────────────────
        subq = (
            sess.query(URL.youtube_url.label("uurl"),
                       Actor.id.label("aid"))
            .join(Token, Token.youtube_url == URL.youtube_url)
            .join(Actor, Actor.name == Token.actor_name)
            .filter(URL.actor_id.is_(None))       # 아직 매핑 안 된 URL
            .subquery()
        )

        updated = (
            sess.execute(
                update(URL)
                .where(URL.youtube_url == subq.c.uurl)
                .values(actor_id=subq.c.aid)
                .execution_options(synchronize_session=False)
            ).rowcount
        )
        sess.commit()
        print(f"\n✅ actor_id 채워 넣은 URL 수: {updated}\n")

        # ── 2. 아직 NULL 인 URL 확인 ─────────────────
        remaining = (
            sess.query(URL.youtube_url, Token.actor_name)
            .join(Token, Token.youtube_url == URL.youtube_url)
            .filter(URL.actor_id.is_(None))
            .all()
        )

        if remaining:
            print("❗ 아직 매핑되지 않은 (youtube_url, actor_name) 목록")
            print(tabulate(remaining, headers=["youtube_url", "actor_name"]))
        else:
            print("🎉 모든 URL이 배우와 매핑되었습니다!")

if __name__ == "__main__":
    main()
