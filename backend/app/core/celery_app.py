"""Celery 应用配置。

- broker 与 result backend 使用 Redis 不同 database（规范 A5）；
- 一期 Windows 部署下使用 threads pool（prefork 依赖 fork 不可用）。
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "sighttest",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,
    task_default_queue="sighttest",
    broker_connection_retry_on_startup=True,
    worker_pool="threads",
)

celery_app.autodiscover_tasks(["app.tasks"])
