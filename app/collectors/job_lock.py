"""
app/collectors/job_lock.py

collector 중복 실행 방지용 파일 잠금

역할:
- 스케줄러, 서버 시작 시 즉시수집, 수동 API 트리거가 같은 collector를
  동시에 실행하지 않도록 파일 잠금으로 막는다.
"""

import os
import time
from contextlib import contextmanager

from app.config import BASE_DIR

LOCK_DIR = BASE_DIR / "storage" / "locks"
LOCK_STALE_SECONDS = 60 * 60 * 2  # 비정상 종료 뒤 잠금이 영구히 남지 않도록 2시간 뒤 재획득 허용


def ensure_lock_dir():
    """
    잠금 파일 보관 폴더를 준비한다.
    """
    LOCK_DIR.mkdir(parents=True, exist_ok=True)


@contextmanager
def collector_lock(lock_name):
    """
    같은 collector가 겹쳐 돌지 않도록 파일 잠금을 건다.
    """
    ensure_lock_dir()
    lock_path = LOCK_DIR / f"{lock_name}.lock"
    lock_fd = None

    try:
        if lock_path.exists():
            lock_age = time.time() - lock_path.stat().st_mtime

            # 비정상 종료로 남은 오래된 lock은 새 실행이 회복할 수 있게 제거한다.
            if lock_age > LOCK_STALE_SECONDS:
                lock_path.unlink(missing_ok=True)

        lock_fd = os.open(
            str(lock_path),
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
        )
        os.write(lock_fd, str(os.getpid()).encode("utf-8"))
        yield True

    except FileExistsError:
        print(f"[SKIP] {lock_name} already running; overlapping execution prevented.")
        yield False

    finally:
        if lock_fd is not None:
            os.close(lock_fd)
            lock_path.unlink(missing_ok=True)
