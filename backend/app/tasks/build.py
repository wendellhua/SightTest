"""方案建设 Celery 任务。

串联「探索 → 产品分析 → 用例生成 → 发布版本」主链路，通过
`self.update_state` 上报进度，token 用量落 `model_call_logs`。
"""

import logging
from datetime import UTC, datetime
from typing import Any

from app.agents.analyze import AnalyzeAgent
from app.agents.case_gen import CaseGenAgent
from app.agents.metrics import record_usage
from app.core.celery_app import celery_app
from app.core.database import sync_session_factory
from app.models import Case, ModelConfig, PlanVersion, Project
from app.runner.browser import BrowserSession

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="build.run", max_retries=0, time_limit=3600)
def run_build(self: Any, build_id: int, project_id: int) -> dict[str, Any]:
    """执行方案建设。"""
    session = sync_session_factory()
    try:
        project = session.get(Project, project_id)
        plan_version = session.get(PlanVersion, build_id)
        if project is None or plan_version is None:
            raise RuntimeError("项目或方案版本不存在")

        model_config = session.get(ModelConfig, project.model_config_id) if project.model_config_id else None
        if model_config is None:
            raise RuntimeError("项目未绑定模型")

        # 1. 探索（TODO: 自动登录后深度探索；当前 MVP 采集首页快照）
        self.update_state(state="PROGRESS", meta={"stage": "explore", "progress": 10})
        with BrowserSession() as browser:
            browser.open(project.url)
            snapshot = browser.snapshot()

        # 2. 产品分析
        self.update_state(state="PROGRESS", meta={"stage": "analyze", "progress": 50})
        analyze_agent = AnalyzeAgent(model_config)
        modules = analyze_agent.run(snapshot)
        record_usage(
            session, project_id, model_config.id, "analyze",
            analyze_agent.usage.input_tokens, analyze_agent.usage.output_tokens,
            task_type="build", task_id=build_id,
        )

        # 3. 用例生成
        self.update_state(state="PROGRESS", meta={"stage": "generate", "progress": 65})
        case_agent = CaseGenAgent(model_config)
        cases = case_agent.run(modules)
        record_usage(
            session, project_id, model_config.id, "case_gen",
            case_agent.usage.input_tokens, case_agent.usage.output_tokens,
            task_type="build", task_id=build_id,
        )

        # 4. 用例落库
        self.update_state(state="PROGRESS", meta={"stage": "generate", "progress": 85})
        for case_data in cases:
            session.add(
                Case(
                    project_id=project_id,
                    plan_version_id=build_id,
                    case_type="func",
                    module_path=case_data.get("module_path"),
                    page=case_data.get("page"),
                    name=case_data.get("name") or "未命名用例",
                    priority=case_data.get("priority") or "P2",
                    precondition=case_data.get("precondition"),
                    steps=case_data.get("steps") or "",
                    expect=case_data.get("expect") or "",
                )
            )

        # 5. 发布版本
        plan_version.explore_data = {"modules": modules, "snapshot": snapshot}
        plan_version.explore_stats = {"pages": 1, "modules": len(modules), "cases": len(cases)}
        plan_version.status = "completed"
        plan_version.completed_at = datetime.now(UTC)
        project.plan_status = "ready"
        session.commit()

        return {"build_id": build_id, "case_count": len(cases), "module_count": len(modules)}

    except Exception:
        logger.exception("方案建设失败 build_id=%s", build_id)
        session.rollback()
        plan_version = session.get(PlanVersion, build_id)
        if plan_version is not None:
            plan_version.status = "failed"
        project = session.get(Project, project_id)
        if project is not None:
            project.plan_status = "build_failed"
        session.commit()
        raise
    finally:
        session.close()
