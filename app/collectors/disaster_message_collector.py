"""
app/collectors/disaster_message_collector.py

긴급재난문자 수집기

역할:
- 외부 재난문자 API 호출
- 응답 데이터 파싱
- 산불/화재 관련 문자만 필터링
- region 매핑
- disaster_message 테이블 저장
- collector_job_log 테이블에 실행 로그 저장

주의:
- 지금 단계는 "구조를 먼저 완성"하는 단계다.
- 실제 API 엔드포인트/파라미터는 발급받은 문서에 맞게 나중에 수정하면 된다.
"""

from datetime import datetime

import requests

from app.config import DISASTER_API_KEY, REQUEST_TIMEOUT
from app.db.session import SessionLocal
from app.db.models.region import Region
from app.db.models.disaster_message import DisasterMessage
from app.db.models.collector_job_log import CollectorJobLog
from app.filters.keyword_filter import (
    contains_disaster_keyword,
    extract_keyword_tag,
    classify_message_type,
)


class DisasterMessageCollector:
    """
    긴급재난문자 수집기 클래스

    왜 클래스로 만드나?
    - 설정값, 요청 함수, 파싱 함수, 저장 함수를 한 객체 안에서 관리하기 쉽다.
    - 나중에 collector가 늘어나도 구조를 맞추기 좋다.
    """

    def __init__(self):
        """
        수집기에 필요한 기본 설정값 초기화
        """
        self.api_key = DISASTER_API_KEY
        self.timeout = REQUEST_TIMEOUT

        """
        실제 API 주소는 나중에 공공데이터포털 문서 기준으로 교체
        지금은 예시 placeholder다.
        """
        self.base_url = "https://example-disaster-api-url"

        """
        수집 작업 이름
        collector_job_log에 어떤 작업인지 기록할 때 사용
        """
        self.job_name = "disaster_message_collector"

    def create_job_log(self, session):
        """
        수집 작업 시작 로그 row 생성
        """
        log = CollectorJobLog(
            job_name=self.job_name,
            job_status="STARTED",
            requested_url=self.base_url,
            response_status_code=None,
            fetched_count=0,
            parsed_count=0,
            saved_count=0,
            skipped_count=0,
            error_message=None,
            started_at=datetime.utcnow(),
            finished_at=None,
        )

        session.add(log)
        session.commit()
        session.refresh(log)

        print(f"[LOG] 작업 로그 생성 완료 - log_id={log.id}")

        return log

    def update_job_log_success(
        self,
        session,
        job_log,
        response_status_code,
        fetched_count,
        parsed_count,
        saved_count,
        skipped_count,
    ):
        """
        수집 작업 성공 로그 업데이트
        """
        job_log.job_status = "SUCCESS"
        job_log.response_status_code = response_status_code
        job_log.fetched_count = fetched_count
        job_log.parsed_count = parsed_count
        job_log.saved_count = saved_count
        job_log.skipped_count = skipped_count
        job_log.finished_at = datetime.utcnow()

        session.commit()

        print(f"[LOG] 작업 로그 성공 업데이트 완료 - log_id={job_log.id}")

    def update_job_log_failed(
        self,
        session,
        job_log,
        error_message,
        response_status_code=None,
        fetched_count=0,
        parsed_count=0,
        saved_count=0,
        skipped_count=0,
    ):
        """
        수집 작업 실패 로그 업데이트
        """
        job_log.job_status = "FAILED"
        job_log.response_status_code = response_status_code
        job_log.fetched_count = fetched_count
        job_log.parsed_count = parsed_count
        job_log.saved_count = saved_count
        job_log.skipped_count = skipped_count
        job_log.error_message = error_message
        job_log.finished_at = datetime.utcnow()

        session.commit()

        print(f"[LOG] 작업 로그 실패 업데이트 완료 - log_id={job_log.id}")

    def fetch_messages(self):
        """
        외부 API에서 재난문자 원본 데이터를 가져오는 함수

        Returns
        -------
        tuple[list, int | None, str | None]
            (원본 데이터 목록, 응답 상태코드, 에러메시지)
            실패 시 ([], None, 에러문자열)
        """
        print("[START] 재난문자 API 호출 시작")

        params = {
            "serviceKey": self.api_key,
            "pageNo": 1,
            "numOfRows": 50,
            "type": "json",
        }

        try:
            response = requests.get(
                self.base_url,
                params=params,
                timeout=self.timeout
            )

            print(f"[INFO] 응답 상태코드: {response.status_code}")

            response.raise_for_status()

            data = response.json()

            # 실제 API 구조에 따라 나중에 수정
            items = data.get("items", [])

            print(f"[DONE] 재난문자 원본 데이터 수신 완료: {len(items)}건")
            return items, response.status_code, None

        except Exception as e:
            print("[ERROR] 재난문자 API 호출 실패")
            print(f"[ERROR DETAIL] {e}")
            return [], None, str(e)

    def parse_message_item(self, item):
        """
        원본 item 1개를 우리 프로젝트 구조에 맞는 dict로 변환
        """
        try:
            region_name = item.get("region_name", "").strip()
            sender = item.get("sender", "").strip()
            message_text = item.get("message_text", "").strip()
            external_message_id = item.get("message_id", None)
            sent_at_raw = item.get("sent_at", "")

            sent_at = datetime.strptime(sent_at_raw, "%Y-%m-%d %H:%M:%S")

            return {
                "external_message_id": external_message_id,
                "region_name": region_name,
                "sender": sender,
                "message_text": message_text,
                "sent_at": sent_at,
            }

        except Exception as e:
            print("[ERROR] 재난문자 파싱 실패")
            print(f"[ERROR DETAIL] {e}")
            print(f"[ERROR ITEM] {item}")
            return None

    def find_region(self, session, region_name):
        """
        region_name 문자열을 기준으로 region 테이블에서 지역 찾기
        """
        return (
            session.query(Region)
            .filter(Region.region_name == region_name)
            .first()
        )

    def is_duplicate(self, session, region_id, sent_at, message_text):
        """
        같은 재난문자가 이미 저장되어 있는지 검사
        """
        existing = (
            session.query(DisasterMessage)
            .filter(
                DisasterMessage.region_id == region_id,
                DisasterMessage.sent_at == sent_at,
                DisasterMessage.message_text == message_text,
            )
            .first()
        )

        return existing is not None

    def save_messages(self, parsed_items):
        """
        파싱된 메시지 목록을 DB에 저장

        Returns
        -------
        tuple[int, int]
            (saved_count, skipped_count)
        """
        print("[START] 재난문자 DB 저장 시작")

        session = SessionLocal()

        saved_count = 0
        skipped_count = 0

        try:
            for item in parsed_items:
                if not item:
                    skipped_count += 1
                    continue

                region_name = item["region_name"]
                message_text = item["message_text"]
                sent_at = item["sent_at"]

                if not contains_disaster_keyword(message_text):
                    skipped_count += 1
                    continue

                region = self.find_region(session, region_name)
                if not region:
                    print(f"[WARN] 지역 매핑 실패: {region_name}")
                    skipped_count += 1
                    continue

                if self.is_duplicate(session, region.id, sent_at, message_text):
                    print(f"[INFO] 중복 문자 건너뜀: {region_name} / {sent_at}")
                    skipped_count += 1
                    continue

                keyword_tag = extract_keyword_tag(message_text)
                message_type = classify_message_type(message_text)

                new_message = DisasterMessage(
                    external_message_id=item["external_message_id"],
                    region_id=region.id,
                    region_name=region.region_name,
                    sender=item["sender"],
                    message_text=message_text,
                    message_type=message_type,
                    keyword_tag=keyword_tag,
                    sent_at=sent_at,
                    source="disaster_api"
                )

                session.add(new_message)
                saved_count += 1

            session.commit()

            print(
                f"[DONE] 재난문자 DB 저장 완료 - 저장: {saved_count}, 건너뜀: {skipped_count}"
            )

            return saved_count, skipped_count

        except Exception as e:
            session.rollback()
            print("[ERROR] 재난문자 DB 저장 중 오류 발생")
            print(f"[ERROR DETAIL] {e}")
            raise

        finally:
            session.close()
            print("[END] 재난문자 DB 세션 종료")

    def collect(self):
        """
        수집기 전체 실행 흐름

        순서:
        1. 작업 로그 생성
        2. API 호출
        3. 원본 파싱
        4. DB 저장
        5. 작업 로그 성공/실패 업데이트
        """
        print("[START] 재난문자 수집 작업 시작")

        log_session = SessionLocal()
        job_log = None

        try:
            job_log = self.create_job_log(log_session)

            raw_items, response_status_code, fetch_error = self.fetch_messages()

            if fetch_error:
                self.update_job_log_failed(
                    session=log_session,
                    job_log=job_log,
                    error_message=fetch_error,
                    response_status_code=response_status_code,
                    fetched_count=0,
                    parsed_count=0,
                    saved_count=0,
                    skipped_count=0,
                )
                print("[DONE] 재난문자 수집 작업 종료 (API 호출 실패)")
                return

            parsed_items = []
            for item in raw_items:
                parsed = self.parse_message_item(item)
                if parsed:
                    parsed_items.append(parsed)

            parsed_count = len(parsed_items)
            fetched_count = len(raw_items)

            print(f"[INFO] 파싱 완료 건수: {parsed_count}")

            saved_count, skipped_count = self.save_messages(parsed_items)

            self.update_job_log_success(
                session=log_session,
                job_log=job_log,
                response_status_code=response_status_code,
                fetched_count=fetched_count,
                parsed_count=parsed_count,
                saved_count=saved_count,
                skipped_count=skipped_count,
            )

            print("[DONE] 재난문자 수집 작업 종료")

        except Exception as e:
            print("[ERROR] 재난문자 수집 작업 전체 실패")
            print(f"[ERROR DETAIL] {e}")

            if job_log:
                self.update_job_log_failed(
                    session=log_session,
                    job_log=job_log,
                    error_message=str(e),
                )

        finally:
            log_session.close()
            print("[END] 로그 세션 종료")