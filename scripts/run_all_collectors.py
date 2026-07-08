"""
scripts/run_all_collectors.py

자동 수집 스케줄러 실행 파일

역할:
- APScheduler로 collector를 주기 실행
- 파일 잠금으로 중복 실행을 방지
- 로컬 개발용 수동 실행 스크립트는 그대로 유지
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import (
    DISASTER_COLLECTION_INTERVAL_MINUTES,
    WILDFIRE_COLLECTION_INTERVAL_MINUTES,
)
from app.collectors.disaster_message_collector import DisasterMessageCollector
from app.collectors.wildfire_risk_collector import WildfireRiskCollector
from app.collectors.job_lock import collector_lock


def run_disaster_collector_job():
    """
    재난문자 collector 스케줄 작업
    """
    with collector_lock("disaster_message_collector") as acquired:
        if not acquired:
            return

        DisasterMessageCollector().collect()


def run_wildfire_collector_job():
    """
    산불위험예보 collector 스케줄 작업
    """
    with collector_lock("wildfire_risk_collector") as acquired:
        if not acquired:
            return

        WildfireRiskCollector().collect()


def main():
    """
    APScheduler 기반 자동 수집 스케줄러 시작
    """
    scheduler = BlockingScheduler(
        job_defaults={
            "coalesce": True,  # 지연된 실행이 쌓이면 최신 한 번으로 합쳐 과도한 연속 실행을 막는다.
            "max_instances": 1,  # 같은 job이 scheduler 내부에서 동시에 두 번 돌지 않게 한다.
            "misfire_grace_time": 300,
        }
    )

    scheduler.add_job(
        run_disaster_collector_job,
        trigger=IntervalTrigger(minutes=DISASTER_COLLECTION_INTERVAL_MINUTES),
        id="disaster_message_collector_job",
        name="Disaster Message Collector",
        replace_existing=True,
    )

    scheduler.add_job(
        run_wildfire_collector_job,
        trigger=IntervalTrigger(minutes=WILDFIRE_COLLECTION_INTERVAL_MINUTES),
        id="wildfire_risk_collector_job",
        name="Wildfire Risk Collector",
        replace_existing=True,
    )

    print(
        "[START] Collector scheduler started "
        f"(disaster={DISASTER_COLLECTION_INTERVAL_MINUTES}m, "
        f"wildfire={WILDFIRE_COLLECTION_INTERVAL_MINUTES}m)"
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("[END] Collector scheduler stopped.")


if __name__ == "__main__":
    main()
