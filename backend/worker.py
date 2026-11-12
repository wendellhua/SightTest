"""Celery Worker 启动入口。

用法（Windows，已默认 threads pool）：
    celery -A worker.celery_app worker --loglevel=info
"""

from app.core.celery_app import celery_app  # noqa: F401
