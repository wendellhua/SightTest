"""调试执行任务。

当前为占位实现（标记完成 + 写用例快照），阶段 6 接入真实 UI 执行引擎
（登录 → 执行步骤 → 断言 → 证据采集）。
"""

import logging
from datetime import UTC, datetime
from typing import Any

from app.core.celery_app import celery_app
from app.core.database import sync_session_factory
from app.models import Case, CaseExecution, Execution

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="debug.run", max_retries=0, time_limit=600)
def run_debug(self: Any, execution_id: int, case_id: int) -> dict[str, Any]:
    """执行单条用例调试。"""
    session = sync_session_factory()
    try:
        execution = session.get(Execution, execution_id)
        case = session.get(Case, case_id)
        if execution is None or case is None:
            raise RuntimeError("执行记录或用例不存在")

        # TODO(阶段 6): 接入真实 UI 执行引擎
        execution.status = "completed"
        execution.progress = 100
        execution.finished_at = datetime.now(UTC)

        session.add(
            CaseExecution(
                case_id=case_id,
                execution_id=execution_id,
                plan_version_id=case.plan_version_id,
                result="pass",
                case_snapshot={
                    "name": case.name,
                    "steps": case.steps,
                    "expect": case.expect,
                    "case_type": case.case_type,
                    "priority": case.priority,
                },
            )
        )
        session.commit()
        return {"execution_id": execution_id}
    finally:
        session.close()
