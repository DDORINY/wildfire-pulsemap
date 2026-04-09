"""
scripts/test_insert_disaster_message.py

disaster_message 테이블에 테스트 데이터를 1건 저장하는 파일

역할:
- region 테이블에서 기준 지역 1건 조회
- 해당 지역에 연결되는 재난문자 1건 생성
- DB에 저장
- 중복 저장 방지 확인

실행 예시:
- python -m scripts.test_insert_disaster_message
"""

from datetime import datetime

from app.db.session import SessionLocal
from app.db.models.region import Region
from app.db.models.disaster_message import DisasterMessage


def insert_test_disaster_message():
    """
    disaster_message 테스트 데이터를 저장하는 함수
    """
    print("[START] DisasterMessage 테스트 데이터 저장을 시작합니다.")

    # DB 세션 생성
    session = SessionLocal()

    try:
        """
        1) 먼저 기준 지역을 찾는다.

        disaster_message 역시 region_id가 필요하기 때문에
        먼저 region 테이블에서 지역을 찾는다.
        """
        region = (
            session.query(Region)
            .filter(
                Region.sido == "강원특별자치도",
                Region.sigungu == "강릉시"
            )
            .first()
        )

        if not region:
            print("[ERROR] 기준 지역(region)을 찾을 수 없습니다.")
            print("[ERROR] 먼저 Region 테스트 데이터를 저장해야 합니다.")
            return

        # Region 모델에 region_name 필드가 없을 수도 있으므로 안전하게 처리
        region_name = getattr(region, "region_name", f"{region.sido} {region.sigungu}")

        """
        2) 테스트용 발송 시각 생성
        """
        sent_at = datetime(2026, 4, 10, 8, 30, 0)

        """
        3) 테스트용 문자 본문 생성
        """
        message_text = "[산불] 강릉시 산불 확산 우려 지역 주민은 안전한 장소로 대피 바랍니다."

        """
        4) 중복 여부 확인

        disaster_message는
        (region_id + sent_at + message_text) 조합이 unique라서
        같은 지역/같은 시각/같은 문자내용이면 중복으로 본다.
        """
        existing_message = (
            session.query(DisasterMessage)
            .filter(
                DisasterMessage.region_id == region.id,
                DisasterMessage.sent_at == sent_at,
                DisasterMessage.message_text == message_text
            )
            .first()
        )

        if existing_message:
            print("[INFO] 이미 저장된 disaster_message 데이터입니다.")
            print(existing_message)
            return

        """
        5) 새 DisasterMessage 객체 생성
        """
        new_message = DisasterMessage(
            external_message_id="TEST-DMSG-001",
            region_id=region.id,
            region_name=region_name,
            sender="행정안전부",
            message_text=message_text,
            message_type="산불",
            keyword_tag="대피",
            sent_at=sent_at,
            source="disaster_api_test"
        )

        # 세션에 추가
        session.add(new_message)

        # 실제 DB 반영
        session.commit()

        # 방금 저장된 row 값 갱신
        session.refresh(new_message)

        print("[DONE] DisasterMessage 테스트 데이터 저장이 완료되었습니다.")
        print(
            f"[RESULT] id={new_message.id}, "
            f"region_name={new_message.region_name}, "
            f"message_type={new_message.message_type}, "
            f"sender={new_message.sender}"
        )

    except Exception as e:
        # 오류 시 트랜잭션 취소
        session.rollback()
        print("[ERROR] DisasterMessage 데이터 저장 중 오류가 발생했습니다.")
        print(f"[ERROR DETAIL] {e}")

    finally:
        # 세션 종료
        session.close()
        print("[END] DB 세션을 종료합니다.")


if __name__ == "__main__":
    insert_test_disaster_message()