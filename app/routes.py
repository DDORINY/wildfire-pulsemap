"""
app/routes.py

Flask 라우트 파일

역할:
- 기본 페이지 렌더링
- DB 테스트 페이지 렌더링
- 프론트에서 사용할 JSON API 제공
"""

from flask import Blueprint, render_template, jsonify

from app.db.session import SessionLocal
from app.db.models import Region, WildfireRisk, DisasterMessage
from app.db.models.collector_job_log import CollectorJobLog

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    """
    메인 지도 페이지
    """
    return render_template("pages/map.html")


@main_bp.route("/db-test")
def db_test():
    """
    DB 연결 테스트용 HTML 페이지
    """
    session = SessionLocal()

    try:
        recent_risks = (
            session.query(WildfireRisk)
            .order_by(WildfireRisk.id.desc())
            .limit(10)
            .all()
        )

        recent_messages = (
            session.query(DisasterMessage)
            .order_by(DisasterMessage.id.desc())
            .limit(10)
            .all()
        )

        return render_template(
            "pages/db_test.html",
            recent_risks=recent_risks,
            recent_messages=recent_messages
        )

    finally:
        session.close()


@main_bp.route("/api/risk/latest")
def api_risk_latest():
    """
    최근 산불 위험도 데이터를 JSON으로 반환하는 API

    역할:
    - 프론트 map.js에서 fetch()로 호출할 수 있게 함
    - 지금은 DB에 저장된 wildfire_risk 데이터를 그대로 JSON 형태로 내려줌
    """
    session = SessionLocal()

    try:
        """
        wildfire_risk 테이블에서 최신 데이터 조회
        id 내림차순으로 정렬해서 최근 데이터부터 가져온다.
        """
        risks = (
            session.query(WildfireRisk)
            .order_by(WildfireRisk.id.desc())
            .limit(50)
            .all()
        )

        result = []

        for risk in risks:
            """
            region relationship을 통해 좌표를 가져온다.
            region이 연결되어 있지 않으면 lat/lng는 None 처리
            """
            lat = risk.region.center_lat if risk.region else None
            lng = risk.region.center_lng if risk.region else None

            result.append({
                "id": risk.id,
                "region_id": risk.region_id,
                "region_name": risk.region_name,
                "risk_score": risk.risk_score,
                "risk_level": risk.risk_level,
                "forecast_time": risk.forecast_time.strftime("%Y-%m-%d %H:%M:%S") if risk.forecast_time else None,
                "source": risk.source,
                "lat": lat,
                "lng": lng
            })

        return jsonify(result)

    finally:
        session.close()

@main_bp.route("/api/messages/latest")
def api_messages_latest():
    """
    최근 재난문자 데이터를 JSON으로 반환하는 API

    역할:
    - 프론트 map.js에서 fetch()로 호출
    - 지도 재난문자 마커
    - 오른쪽 최근 재난문자 목록
    에 사용할 데이터를 JSON으로 제공
    """
    session = SessionLocal()

    try:
        """
        disaster_message 테이블에서 최근 데이터 조회
        """
        messages = (
            session.query(DisasterMessage)
            .order_by(DisasterMessage.id.desc())
            .limit(50)
            .all()
        )

        result = []

        for msg in messages:
            """
            region relationship을 통해 좌표를 가져온다.
            """
            lat = msg.region.center_lat if msg.region else None
            lng = msg.region.center_lng if msg.region else None

            result.append({
                "id": msg.id,
                "external_message_id": msg.external_message_id,
                "region_id": msg.region_id,
                "region_name": msg.region_name,
                "sender": msg.sender,
                "message_text": msg.message_text,
                "message_type": msg.message_type,
                "keyword_tag": msg.keyword_tag,
                "sent_at": msg.sent_at.strftime("%Y-%m-%d %H:%M:%S") if msg.sent_at else None,
                "source": msg.source,
                "lat": lat,
                "lng": lng
            })

        return jsonify(result)

    finally:
        session.close()

@main_bp.route("/job-log-test")
def job_log_test():
    """
    수집 실행 로그 확인용 HTML 페이지

    역할:
    - collector_job_log 테이블의 최근 로그를 조회
    - 웹 화면에서 성공/실패 여부와 에러 메시지를 확인
    """
    session = SessionLocal()

    try:
        """
        최신 로그부터 30건 조회
        """
        recent_logs = (
            session.query(CollectorJobLog)
            .order_by(CollectorJobLog.id.desc())
            .limit(30)
            .all()
        )

        return render_template(
            "pages/job_log_test.html",
            recent_logs=recent_logs
        )

    finally:
        session.close()