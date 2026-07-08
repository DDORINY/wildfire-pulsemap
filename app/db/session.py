"""
app/db/session.py

DB 연결 엔진과 세션을 만드는 파일

역할:
- SQLite DB와 실제 연결
- DB 작업용 세션(Session) 생성
- 나중에 insert, select, update 할 때 이 세션을 사용
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import DATABASE_URL

# create_engine:
# 실제 DB와 연결하는 엔진 객체를 생성
#
# echo=False:
# SQL 실행문을 콘솔에 전부 출력하지 않음
# 디버깅할 때 보고 싶으면 True로 바꿔도 됨
#
# future=True:
# SQLAlchemy 2.x 스타일에 맞게 동작하도록 설정
connect_args = {}

# 서버 시작 시 백그라운드 수집 스레드와 요청 처리가 동시에 SQLite에 접근할 수 있어서,
# 짧은 잠금 충돌 정도는 예외 대신 잠깐 대기 후 재시도하도록 timeout을 늘려둔다.
if DATABASE_URL.startswith("sqlite:///"):
    connect_args["timeout"] = 15

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args=connect_args,
)

# sessionmaker:
# DB 작업용 세션 공장
# 필요할 때 SessionLocal()을 호출해서 세션 객체를 만듦
SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine,
    future=True
)