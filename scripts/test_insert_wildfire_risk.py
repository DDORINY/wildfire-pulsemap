"""
scripts/test_insert_wildfire_risk.py

wildfire_risk 테이블에 테스트 데이터를 1건 저장하는 파일

역할:
- region 테이블에서 기준 지역 1건을 조회
- 그 지역에 연결되는 산불 위험 예보 데이터를 1건 생성
- DB에 저장
- 중복 저장 방지 확인

실행 예시:
- python -m scripts.test_insert_wildfire_risk
"""

from datetime import datetime

from app.db.session import SessionLocal
from app.db.models.region import Region
from app.db.models.wildfire_risk import WildfireRisk


def insert_test_wildfire_risk():
    """
    wildfire_risk 테스트 데이터를 저장하는 함수
    """
    print("[START] WildfireRisk 테스트 데이터 저장을 시작합니다.")

    # DB 세션 생성
    session = SessionLocal()

    try:
        """
        1) 먼저 기준이 되는 region 데이터를 찾는다.

        왜 먼저 찾나?
        - wildfire_risk는 region_id가 꼭 필요하다.
        - 즉, 어느 지역의 위험도인지 먼저 알아야 저장 가능하다.
        """
        region = (
            session.query(Region)
            .filter(
                Region.sido == "강원특별자치도",
                Region.sigungu == "강릉시"
            )
            .first()
        )

        # region이 없으면 테스트를 진행할 수 없다.
        if not region:
            print("[ERROR] 기준 지역(region)을 찾을 수 없습니다.")
            print("[ERROR] 먼저 Region 테스트 데이터를 저장해야 합니다.")
            return

        # Region 모델에 region_name 필드가 없을 수도 있으므로 안전하게 처리
        region_name = getattr(region, "region_name", f"{region.sido} {region.sigungu}")

        """
        2) 예보 기준 시각을 하나 만든다.

        이 값은 중복 방지에도 중요하다.
        wildfire_risk는 (region_id + forecast_time) 조합이 unique라서
        같은 지역, 같은 시각 데이터는 두 번 저장되면 안 된다.
        """
        forecast_time = datetime(2026, 4, 10, 9, 0, 0)

        """
        3) 이미 같은 데이터가 저장되어 있는지 먼저 확인한다.

        이유:
        - 중복 저장 시 UNIQUE 제약조건 오류가 날 수 있다.
        - 따라서 먼저 조회해서 있으면 저장하지 않는다.
        """
        existing_risk = (
            session.query(WildfireRisk)
            .filter(
                WildfireRisk.region_id == region.id,
                WildfireRisk.forecast_time == forecast_time
            )
            .first()
        )

        if existing_risk:
            print("[INFO] 이미 저장된 wildfire_risk 데이터입니다.")
            print(existing_risk)
            return

        """
        4) 새 WildfireRisk 객체 생성

        region_id:
        - region 테이블의 id 연결

        region_name:
        - 원본 문자열 그대로 저장

        risk_score:
        - 예시 점수

        risk_level:
        - 예시 등급

        forecast_time:
        - 예보 기준 시각
        """
        new_risk = WildfireRisk(
            region_id=region.id,
            region_name=region_name,
            risk_score=82.5,
            risk_level="매우 높음",
            forecast_time=forecast_time,
            source="forest_api_test"
        )

        # 세션에 추가
        session.add(new_risk)

        # 실제 DB 반영
        session.commit()

        # 방금 저장된 값 다시 반영
        session.refresh(new_risk)

        print("[DONE] WildfireRisk 테스트 데이터 저장이 완료되었습니다.")
        print(
            f"[RESULT] id={new_risk.id}, "
            f"region_name={new_risk.region_name}, "
            f"risk_level={new_risk.risk_level}, "
            f"risk_score={new_risk.risk_score}"
        )

    except Exception as e:
        """
        오류 발생 시 rollback 수행

        이유:
        - commit 중 오류가 나면 현재 트랜잭션 상태를 정리해야 한다.
        """
        session.rollback()
        print("[ERROR] WildfireRisk 데이터 저장 중 오류가 발생했습니다.")
        print(f"[ERROR DETAIL] {e}")

    finally:
        # 세션 정리
        session.close()
        print("[END] DB 세션을 종료합니다.")


if __name__ == "__main__":
    insert_test_wildfire_risk()