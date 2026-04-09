"""
app/config.py

프로젝트 전역 설정 파일

역할:
- .env 파일에서 환경변수 로드
- DB 연결 주소 관리
- 외부 API 키 관리
- 수집기 공통 설정 관리
"""

import os

from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

"""
DATABASE_URL:
- SQLite 또는 나중에 PostgreSQL 주소를 환경변수로 관리
- 환경변수가 없으면 기본값으로 SQLite 사용
"""
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///storage/pulsemap.db")

"""
외부 공공데이터 API 키
- 지금은 비어 있어도 됨
- 나중에 실제 API 발급받으면 .env에 넣으면 됨
"""
DISASTER_API_KEY = os.getenv("DISASTER_API_KEY", "")
WILDFIRE_API_KEY = os.getenv("WILDFIRE_API_KEY", "")

"""
REQUEST_TIMEOUT:
- 외부 API 요청 제한 시간(초)
- 환경변수 값이 문자열로 들어오므로 int 변환
"""
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))