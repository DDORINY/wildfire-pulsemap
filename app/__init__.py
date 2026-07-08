import threading

from flask import Flask


def create_app():
    """
    Flask 앱 생성 함수

    역할:
    - Flask 앱 객체 생성
    - 라우트(Blueprint) 등록
    - 나중에 config, DB, 확장기능 연결 시 이 함수 안에서 확장 가능
    """
    app = Flask(__name__)

    # Render 같은 서버리스/재배포 환경은 DB 파일이 매 배포마다 새로 생겨서
    # 테이블/지역 시드가 없으면 collector가 전부 저장 실패한다. 앱이 뜰 때마다 보장한다.
    ensure_db_ready()

    # routes.py에 정의한 Blueprint 연결
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    # 배포 직후 지도에 데이터가 하나도 없는 상태를 피하기 위해
    # 서버 시작과 동시에 산불위험예보 최신 데이터를 한 번 수집한다.
    trigger_startup_wildfire_collect()

    return app


def ensure_db_ready():
    """
    DB 테이블 생성과 시도/시군구 region 시드를 앱 시작 시마다 보장한다.

    gunicorn이 worker를 여러 개 띄우면 create_app()이 worker 수만큼
    동시에 실행되는데, 그때마다 267개 region upsert를 동시에 돌리면
    SQLite 쓰기 경합("database is locked")만 키운다. 한 worker만
    실행하고 나머지는 건너뛰도록 락으로 감싼다 (idempotent라 스킵해도 안전).
    """
    from app.collectors.job_lock import collector_lock
    from app.db.init_db import init_db
    from scripts.seed_sido_regions import main as seed_sido_regions

    with collector_lock("app_startup_db_init") as acquired:
        if acquired:
            init_db()
            seed_sido_regions()


def trigger_startup_wildfire_collect():
    """
    산불위험예보 collector를 백그라운드 스레드에서 즉시 1회 실행한다.

    별도 스레드로 돌리는 이유:
    - 외부 API 호출이 느려지거나 실패해도 앱 부팅/요청 응답을 막지 않기 위해서다.
    - collector_lock으로 감싸서 스케줄러나 수동 버튼 호출과 겹쳐도 중복 수집되지 않는다.
    """
    from app.collectors.job_lock import collector_lock
    from app.collectors.wildfire_risk_collector import WildfireRiskCollector

    def run():
        with collector_lock("wildfire_risk_collector") as acquired:
            if acquired:
                WildfireRiskCollector().collect()

    threading.Thread(target=run, daemon=True).start()