"""
app/db/models/wildfire_risk.py

산불 위험 예보 데이터를 저장하는 테이블 모델

역할:
- 시군구별 산불 위험 점수 저장
- 위험 등급 저장
- 예보 기준 시각 저장
- 수집 시각 저장
- 지역(region) 테이블과 연결해서 관리

이 테이블은 나중에 지도에서
"어느 지역이 현재 위험한가?" 를 보여줄 때 핵심이 된다.
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class WildfireRisk(Base):
    """
    WildfireRisk 테이블 모델

    실제 DB 테이블 이름: wildfire_risk
    """

    __tablename__ = "wildfire_risk"

    """
    id:
    - 기본 키
    - 자동 증가 정수
    """
    id = Column(Integer, primary_key=True, autoincrement=True)

    """
    region_id:
    - region 테이블의 id를 참조하는 외래키(FK)
    - 위험도 데이터가 어느 지역에 속하는지 연결
    - region.id 와 연결된다
    """
    region_id = Column(Integer, ForeignKey("region.id"), nullable=False)

    """
    region_name:
    - 외부 API 원문 지역명을 문자열 그대로 저장
    - 예: "강원특별자치도 강릉시"
    - 왜 따로 저장하냐면:
      1) 원본 데이터 추적용
      2) region 매핑이 잘못됐는지 디버깅하기 쉬움
    """
    region_name = Column(String(120), nullable=False)

    """
    risk_score:
    - 산불 위험 점수
    - 예: 82.5
    - Float 사용
    """
    risk_score = Column(Float, nullable=False)

    """
    risk_level:
    - 산불 위험 등급
    - 예: "낮음", "보통", "높음", "매우 높음"
    - 처음에는 문자열로 저장하는 것이 가장 단순하고 보기 쉽다
    """
    risk_level = Column(String(30), nullable=False)

    """
    forecast_time:
    - 예보 기준 시각
    - "이 위험 정보가 어떤 시각 기준 예보인지" 저장
    - 매우 중요함
    - 예: 2026-04-09 18:00
    """
    forecast_time = Column(DateTime, nullable=False)

    """
    source:
    - 데이터 출처
    - 나중에 여러 데이터 소스를 붙일 수 있으므로 남겨두는 것이 좋다
    - 예: "forest_api"
    """
    source = Column(String(50), nullable=False, default="forest_api")

    """
    collected_at:
    - 실제로 우리가 이 데이터를 수집한 시각
    - forecast_time 과 다르다
    - 예보 기준 시각과 수집 시각은 분리해서 저장해야 한다
    """
    collected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    """
    created_at:
    - DB에 이 행(row)이 생성된 시각
    - collected_at과 거의 비슷할 수 있지만 의미를 분리해서 두는 편이 안전하다
    """
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    """
    region 관계 설정

    역할:
    - WildfireRisk 객체에서 연결된 Region 객체를 쉽게 참조 가능
    - 예: wildfire_risk.region.region_name
    """
    region = relationship("Region", back_populates="wildfire_risks")

    """
    중복 방지 제약조건

    region_id + forecast_time 조합은
    중복 저장되지 않게 제한한다.

    이유:
    - 같은 지역
    - 같은 예보 시각 데이터가 여러 번 수집되면
      중복 저장될 수 있기 때문
    """
    __table_args__ = (
        UniqueConstraint(
            "region_id",
            "forecast_time",
            name="uq_wildfire_risk_region_forecast_time",
        ),
    )

    def __repr__(self):
        """
        디버깅할 때 객체를 보기 쉽게 문자열로 표현
        """
        return (
            f"<WildfireRisk(id={self.id}, "
            f"region_name='{self.region_name}', "
            f"risk_level='{self.risk_level}')>"
        )