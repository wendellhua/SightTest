"""Celery 任务模块。导入各任务子模块以完成任务注册。"""

from app.tasks import build, debug, execution, report  # noqa: F401
