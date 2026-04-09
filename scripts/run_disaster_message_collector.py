"""
scripts/run_disaster_message_collector.py
"""

from app.collectors.disaster_message_collector import DisasterMessageCollector


def main():
    collector = DisasterMessageCollector()
    collector.collect()


if __name__ == "__main__":
    main()