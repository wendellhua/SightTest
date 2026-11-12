"""模型调用计量落库。

Celery Worker 内使用同步会话（规范 A3），本模块提供同步落库函数。
"""

from sqlalchemy.orm import Session

from app.models import ModelCallLog


def record_usage(
    session: Session,
    project_id: int | None,
    model_config_id: int | None,
    agent: str,
    input_tokens: int,
    output_tokens: int,
    task_type: str | None = None,
    task_id: int | None = None,
) -> None:
    """写入一条模型调用计量记录。"""
    session.add(
        ModelCallLog(
            project_id=project_id,
            model_config_id=model_config_id,
            agent=agent,
            task_type=task_type,
            task_id=task_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
    )
    session.commit()
