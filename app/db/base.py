"""
app/db/base.py

SQLAlchemy의 Base를 선언하는 파일

역할:
- 앞으로 만들 모든 테이블 모델의 부모 클래스 역할
- region.py, wildfire_risk.py 같은 모델 파일들이 이 Base를 상속받아서 테이블이 됨
"""

from sqlalchemy.orm import declarative_base

# 모든 ORM 모델이 상속받을 기본 클래스
Base = declarative_base()