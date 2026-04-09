"""
app/db/models/disaster_message.py

긴급재난문자 데이터를 저장하는 테이블 모델

역할:
- 실제 발송된 재난문자 저장
- 어느 지역(region)에 대한 문자였는지 연결
- 문자 내용 저장
- 발송 시각 저장
- 어떤 키워드로 분류됐는지 저장
- 중복 수집 방지를 위한 기준 필드 저장

이 테이블은 나중에 지도에서
"실제로 최근 어떤 재난문자가 발송됐는가?" 를 보여줄 때 핵심이 된다.
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class DisasterMessage(Base):
    """
    DisasterMessage 테이블 모델

    실제 DB 테이블 이름: disaster_message
    """

    __tablename__ = "disaster_message"

    """
    id:
    - 기본 키(PK)
    - 자동 증가 정수
    """
    id = Column(Integer, primary_key=True, autoincrement=True)

    """
    external_message_id:
    - 외부 API에서 제공하는 문자 고유 ID가 있으면 저장하는 필드
    - 나중에 같은 문자가 중복 수집됐는지 비교할 때 매우 유용함
    - 처음에는 없어도 될 수 있으므로 nullable=True
    """
    external_message_id = Column(String(100), nullable=True)

    """
    region_id:
    - region 테이블과 연결되는 외래키(FK)
    - 이 재난문자가 어느 지역에 대한 것인지 연결
    """
    region_id = Column(Integer, ForeignKey("region.id"), nullable=False)

    """
    region_name:
    - 외부 API 응답에서 받은 원본 지역명
    - 예: "강원특별자치도 강릉시"
    - region_id와 별도로 저장하는 이유:
      1) 원본 추적
      2) 지역 매핑 오류 디버깅
    """
    region_name = Column(String(120), nullable=False)

    """
    sender:
    - 발송 기관
    - 예: 행정안전부, 강원특별자치도, 강릉시청
    """
    sender = Column(String(100), nullable=True)

    """
    message_text:
    - 실제 재난문자 본문
    - 길 수 있으므로 Text 사용
    """
    message_text = Column(Text, nullable=False)

    """
    message_type:
    - 메시지 분류 결과
    - 예: "산불", "화재", "대피", "통제"
    - 나중에 필터링용으로 사용
    """
    message_type = Column(String(50), nullable=True)

    """
    keyword_tag:
    - 어떤 키워드 때문에 이 문자를 저장했는지 기록
    - 예: "산불", "화재", "대피"
    - message_type과 비슷해 보이지만,
      message_type은 분류 결과,
      keyword_tag는 실제 탐지 키워드라고 보면 된다.
    """
    keyword_tag = Column(String(100), nullable=True)

    """
    sent_at:
    - 실제 재난문자가 발송된 시각
    - 매우 중요한 시간 필드
    """
    sent_at = Column(DateTime, nullable=False)

    """
    source:
    - 데이터 출처
    - 예: "disaster_api"
    - 나중에 다른 출처가 추가될 가능성을 고려해서 필드 분리
    """
    source = Column(String(50), nullable=False, default="disaster_api")

    """
    collected_at:
    - 우리가 이 문자를 수집한 시각
    - sent_at(실제 발송 시각)과 구분해야 함
    """
    collected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    """
    created_at:
    - DB row 생성 시각
    """
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    """
    region 관계 설정

    예: disaster_message.region.region_name 처럼
    연결된 Region 객체를 참조 가능
    """
    region = relationship("Region", back_populates="disaster_messages")

    """
    중복 방지 제약조건

    외부 message id가 없을 수도 있기 때문에
    (region_id, sent_at, message_text) 조합으로 중복을 막는다.

    이유:
    - 같은 지역
    - 같은 시각
    - 같은 문자 내용

    이면 사실상 동일 문자로 볼 수 있기 때문
    """
    __table_args__ = (
        UniqueConstraint(
            "region_id",
            "sent_at",
            "message_text",
            name="uq_disaster_message_region_sent_text",
        ),
    )

    def __repr__(self):
        """
        디버깅할 때 보기 쉽게 문자열 형태로 출력
        """
        return (
            f"<DisasterMessage(id={self.id}, "
            f"region_name='{self.region_name}', "
            f"message_type='{self.message_type}')>"
        )