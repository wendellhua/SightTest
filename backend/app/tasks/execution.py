"""测试执行 Celery 任务。

MVP 执行链路：打开首页采集快照 → 逐用例 UI 判定（LLM）→ 主动发现（LLM）→ 汇总。
接口/压测/机制三类执行引擎在后续迭代接入（当前标 blocked）。
"""

import logging
from datetime import datetime, timezone

from app.agents.discover import DiscoverAgent
from app.agents.judge import JudgeAgent
from app.agents.metrics import record_usage
from app.core.celery_app import celery_app
from app.core.database import sync_session_factory
from app.models import Case, CaseExecution, Execution, Issue, ModelConfig, Project
from app.runner.browser import BrowserSession

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="execution.run", max_retries=0, time_limit=7200)
def run_execution(self, execution_id: int, project_id: int) -> dict:
    """执行测试任务。"""
    session = sync_session_factory()
    try:
        execution = session.get(Execution, execution_id)
        project = session.get(Project, project_id)
        if execution is None or project is None:
            raise RuntimeError("执行记录或项目不存在")

        model_config = session.get(ModelConfig, project.model_config_id) if project.model_config_id else None
        if model_config is None:
            raise RuntimeError("项目未绑定模型")

        execution.status = "running"
        execution.started_at = datetime.now(timezone.utc)
        session.commit()

        # 1. 打开首页采集快照
        self.update_state(state="PROGRESS", meta={"stage": "setup", "progress": 5})
        with BrowserSession() as browser:
            browser.open(project.url)
            snapshot = browser.snapshot()

        execution.progress = 5
        session.commit()

        judge_agent = JudgeAgent(model_config)
        case_ids = list(execution.order_items or [])
        total = max(len(case_ids), 1)
        results: dict[str, int] = {"pass": 0, "fail": 0, "blocked": 0}
        run_summary: list[dict] = []

        # 2. 逐用例判定
        for index, case_id in enumerate(case_ids):
            case = session.get(Case, case_id)
            if case is None:
                continue

            if case.case_type == "func":
                judge_result = judge_agent.run(
                    snapshot,
                    {"name": case.name, "steps": case.steps, "expect": case.expect},
                )
            else:
                # TODO(阶段 6 迭代): 接入接口/压测/机制执行引擎
                judge_result = {"result": "blocked", "reason": "该类型执行引擎待完善"}

            result = judge_result.get("result", "blocked")
            if result not in results:
                result = "blocked"
            results[result] += 1

            case.result = result
            session.add(
                CaseExecution(
                    case_id=case_id,
                    execution_id=execution_id,
                    plan_version_id=case.plan_version_id,
                    result=result,
                    evidence={"reason": judge_result.get("reason", "")},
                    case_snapshot={
                        "name": case.name,
                        "steps": case.steps,
                        "expect": case.expect,
                        "case_type": case.case_type,
                        "priority": case.priority,
                    },
                    started_at=datetime.now(timezone.utc),
                    finished_at=datetime.now(timezone.utc),
                )
            )
            run_summary.append({"name": case.name, "result": result, "reason": judge_result.get("reason", "")})
            progress = int((index + 1) / total * 85)
            self.update_state(state="PROGRESS", meta={"stage": "run", "progress": progress})
            execution.progress = progress
            session.commit()

        record_usage(
            session, project_id, model_config.id, "judge",
            judge_agent.usage.input_tokens, judge_agent.usage.output_tokens,
            task_type="execution", task_id=execution_id,
        )

        # 3. 主动发现
        self.update_state(state="PROGRESS", meta={"stage": "discover", "progress": 92})
        execution.progress = 92
        session.commit()
        discover_agent = DiscoverAgent(model_config)
        issues = discover_agent.run(snapshot, run_summary)
        for issue in issues:
            session.add(
                Issue(
                    project_id=project_id,
                    execution_id=execution_id,
                    page=issue.get("page") or project.url,
                    severity=issue.get("severity") or "low",
                    description=issue.get("description") or "",
                )
            )
        record_usage(
            session, project_id, model_config.id, "discover",
            discover_agent.usage.input_tokens, discover_agent.usage.output_tokens,
            task_type="execution", task_id=execution_id,
        )

        # 4. 完成
        execution.status = "completed"
        execution.progress = 100
        execution.summary = results
        execution.finished_at = datetime.now(timezone.utc)
        session.commit()

        return {"execution_id": execution_id, "summary": results, "issue_count": len(issues)}

    except Exception:
        logger.exception("测试执行失败 execution_id=%s", execution_id)
        session.rollback()
        execution = session.get(Execution, execution_id)
        if execution is not None:
            execution.status = "failed"
            execution.finished_at = datetime.now(timezone.utc)
        session.commit()
        raise
    finally:
        session.close()
