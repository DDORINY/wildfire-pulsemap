"""
app/db/models/region.py

지역 기준 테이블 모델

역할:
- 시도 / 시군구 기준 정보를 저장
- 산불 위험도 데이터와 재난문자를 지역 기준으로 연결할 때 사용
- 나중에 지도 중심 좌표(위도/경도)도 함께 저장 가능

예시:
- 강원특별자치도 / 강릉시
- 경상북도 / 안동시
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class Region(Base):
    """
    Region 테이블 모델

    __tablename__:
    - 실제 DB에 생성될 테이블 이름
    """

    __tablename__ = "region"

    """
    id:
    - 기본 키(PK)
    - 지역 하나를 구분하는 내부 식별자
    - 자동 증가 정수
    """
    id = Column(Integer, primary_key=True, autoincrement=True)

    """
    sido:
    - 시도 이름
    - 예: 강원특별자치도, 경상북도, 서울특별시
    - 필수값이므로 nullable=False
    """
    sido = Column(String(50), nullable=False)

    """
    sigungu:
    - 시군구 이름
    - 예: 강릉시, 안동시, 종로구
    - 필수값
    """
    sigungu = Column(String(50), nullable=False)

    """
    region_name:
    - 화면이나 원본 데이터와 비교할 때 쓰기 쉬운 전체 지역명
    - 예: 강원특별자치도 강릉시
    - 처음에는 문자열 그대로 저장해두면 디버깅할 때 편함
    """
    region_name = Column(String(120), nullable=False)

    """
    region_code:
    - 행정구역 코드나 내부 코드 저장용
    - 지금은 없어도 되지만 나중 확장성을 위해 남겨둠
    - 선택값이라 nullable=True
    """
    region_code = Column(String(30), nullable=True)

    """
    center_lat:
    - 지도에서 해당 지역 중심점 위도
    - 나중에 마커/중심점 표시할 때 사용
    - 처음에는 값이 없어도 되므로 nullable=True
    """
    center_lat = Column(Float, nullable=True)

    """
    center_lng:
    - 지도에서 해당 지역 중심점 경도
    - 처음에는 없어도 됨
    """
    center_lng = Column(Float, nullable=True)

    """
    created_at:
    - 이 지역 데이터가 DB에 처음 저장된 시각
    - 기본값은 현재 시각
    """
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    """
    wildfire_risks:
    - 이 지역과 연결된 산불 위험도 데이터 목록
    - WildfireRisk.region 과 양방향 연결
    """
    wildfire_risks = relationship("WildfireRisk", back_populates="region")

    """
    disaster_messages:
    - 이 지역과 연결된 재난문자 데이터 목록
    - DisasterMessage.region 과 양방향 연결
    """
    disaster_messages = relationship("DisasterMessage", back_populates="region")

    """
    __table_args__:
    - (sido, sigungu) 조합은 중복되지 않게 제한
    - 예를 들어 "강원특별자치도 + 강릉시"가 두 번 들어가면 안 됨
    """
    __table_args__ = (
        UniqueConstraint("sido", "sigungu", name="uq_region_sido_sigungu"),
    )

    def __repr__(self):
        """
        디버깅할 때 객체를 보기 쉽게 문자열로 표현
        """
        return f"<Region(id={self.id}, region_name='{self.region_name}')>"