"""
scripts/test_insert_region.py

Region 테이블에 테스트 데이터를 1건 저장해보는 파일

역할:
- DB 세션이 정상적으로 열리는지 확인
- region 테이블에 insert가 되는지 확인
- 나중에 수집 데이터를 저장하기 전에 가장 먼저 해보는 기본 테스트

실행 예시:
- python scripts/test_insert_region.py
"""

# DB 세션 생성용
from app.db.session import SessionLocal

# Region 모델 import
from app.db.models.region import Region


def insert_test_region():
    """
    테스트용 지역 데이터 1건을 저장하는 함수
    """

    print("[START] Region 테스트 데이터 저장을 시작합니다.")

    # SessionLocal()로 실제 DB 작업 세션 생성
    session = SessionLocal()

    try:
        """
        먼저 중복 여부 확인

        이유:
        - 이미 같은 지역이 들어가 있으면 UNIQUE 제약조건에 걸릴 수 있음
        - sido + sigungu 조합은 중복 저장되지 않게 설계했기 때문
        """
        existing_region = (
            session.query(Region)
            .filter(
                Region.sido == "강원특별자치도",
                Region.sigungu == "강릉시"
            )
            .first()
        )

        if existing_region:
            print("[INFO] 이미 저장된 지역입니다.")
            print(existing_region)
            return

        """
        저장할 Region 객체 생성
        """
        new_region = Region(
            sido="강원특별자치도",
            sigungu="강릉시",
            region_name="강원특별자치도 강릉시",
            region_code="42150",
            center_lat=37.7519,
            center_lng=128.8761
        )

        # 세션에 추가
        session.add(new_region)

        # 실제 DB에 반영
        session.commit()

        # 방금 저장된 데이터 다시 읽기 쉽게 새로고침
        session.refresh(new_region)

        print("[DONE] Region 테스트 데이터 저장이 완료되었습니다.")
        print(
            f"[RESULT] id={new_region.id}, "
            f"region_name={new_region.region_name}"
        )

    except Exception as e:
        """
        오류가 나면 DB 반영 취소
        """
        session.rollback()
        print("[ERROR] Region 데이터 저장 중 오류가 발생했습니다.")
        print(f"[ERROR DETAIL] {e}")

    finally:
        """
        세션은 항상 닫아주는 것이 좋다
        """
        session.close()
        print("[END] DB 세션을 종료합니다.")


if __name__ == "__main__":
    insert_test_region()