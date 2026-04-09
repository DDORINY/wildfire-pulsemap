"""
scripts/run_wildfire_risk_collector.py

산불위험예보 수집기 실행 파일
"""

from app.collectors.wildfire_risk_collector import WildfireRiskCollector


def main():
    collector = WildfireRiskCollector()
    collector.collect()


if __name__ == "__main__":
    main()