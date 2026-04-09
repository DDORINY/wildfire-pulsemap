"""
scripts/test_keyword_filter.py

재난문자 키워드 필터 테스트 파일

실행 예시:
- python -m scripts.test_keyword_filter
"""

from app.filters.keyword_filter import (
    contains_disaster_keyword,
    extract_keyword_tag,
    classify_message_type,
)


def run_test():
    test_messages = [
        "[산불] 강릉시 산불 확산 우려 지역 주민은 안전한 장소로 대피 바랍니다.",
        "[화재] 인근 공장 화재 발생, 차량 우회 바랍니다.",
        "[훈련] 오늘 민방위 훈련이 있습니다.",
        "일반 안내 문자입니다.",
    ]

    for message in test_messages:
        print("=" * 70)
        print("원문:", message)
        print("포함 여부:", contains_disaster_keyword(message))
        print("탐지 키워드:", extract_keyword_tag(message))
        print("분류 결과:", classify_message_type(message))


if __name__ == "__main__":
    run_test()