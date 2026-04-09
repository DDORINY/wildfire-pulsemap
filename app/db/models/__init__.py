"""
app/db/models/__init__.py

모델 패키지 초기화 파일

역할:
- models 폴더를 파이썬 패키지로 인식하게 함
- 나중에 여러 모델을 한 곳에서 import 할 때 사용 가능
"""

from app.db.models.region import Region
from app.db.models.wildfire_risk import WildfireRisk
from app.db.models.disaster_message import DisasterMessage
from app.db.models.collector_job_log import CollectorJobLog