"""
app/filters/keyword_filter.py

재난문자 본문에서 산불/화재 관련 키워드를 판별하는 필터 파일

역할:
- 긴급재난문자 전체 중에서 산불/화재/대피/통제 관련 문자만 골라내기
- 문자 유형(message_type)과 키워드(keyword_tag) 분류에 사용

이 파일은 나중에 collector에서 재난문자 본문을 읽은 뒤
저장할지 말지 결정하는 핵심 로직이 된다.
"""

"""
포함 키워드 목록 설명:
- 이 단어들이 문자 본문에 들어 있으면 산불/화재 관련 재난문자로 판단할 가능성이 높다.
- 처음에는 단순 포함 여부로 시작하고, 나중에 필요하면 정교하게 확장 가능
"""
INCLUDE_KEYWORDS = [
    "산불",
    "화재",
    "대피",
    "통제",
    "입산금지",
    "연기",
    "소각금지",
]

"""
제외 키워드 목록 설명:
- 특정 키워드는 들어 있어도 우리가 원하는 산불/화재 유형이 아닐 수 있다.
- 처음에는 비워두거나 최소만 넣고 시작해도 된다.
"""
EXCLUDE_KEYWORDS = [
    # 예시:
    # "훈련"
]


def contains_disaster_keyword(message_text: str) -> bool:
    """
    문자 본문이 산불/화재 관련 키워드를 포함하는지 판별하는 함수

    Parameters
    ----------
    message_text : str
        재난문자 본문

    Returns
    -------
    bool
        저장 대상이면 True, 아니면 False
    """
    # None 방지
    if not message_text:
        return False

    # 양쪽 공백 제거
    text = message_text.strip()

    # 제외 키워드가 있으면 먼저 탈락
    for keyword in EXCLUDE_KEYWORDS:
        if keyword in text:
            return False

    # 포함 키워드가 하나라도 있으면 통과
    for keyword in INCLUDE_KEYWORDS:
        if keyword in text:
            return True

    return False


def extract_keyword_tag(message_text: str) -> str | None:
    """
    문자 본문에서 실제 탐지된 키워드를 하나 반환하는 함수

    예:
    - "[산불] 강릉시 주민 대피 바랍니다" -> "산불"
    - "화재 확산 우려로 통제 중" -> "화재"

    가장 먼저 발견된 키워드 하나를 반환한다.
    없으면 None 반환
    """
    if not message_text:
        return None

    text = message_text.strip()

    for keyword in INCLUDE_KEYWORDS:
        if keyword in text:
            return keyword

    return None


def classify_message_type(message_text: str) -> str | None:
    """
    문자 본문을 간단한 유형으로 분류하는 함수

    규칙:
    - "산불" 포함 -> "산불"
    - "화재" 포함 -> "화재"
    - "대피" 포함 -> "대피"
    - "통제" 포함 -> "통제"
    - 그 외 포함 키워드만 있으면 "기타"

    Returns
    -------
    str | None
        분류 결과 문자열
    """
    if not message_text:
        return None

    text = message_text.strip()

    if "산불" in text:
        return "산불"

    if "화재" in text:
        return "화재"

    if "대피" in text:
        return "대피"

    if "통제" in text:
        return "통제"

    if contains_disaster_keyword(text):
        return "기타"

    return None