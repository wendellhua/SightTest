"""报告生成任务：摘要 Agent 撰写结论摘要。"""

import logging
from typing import Any

from app.agents.metrics import record_usage
from app.agents.summary import SummaryAgent
from app.core.celery_app import celery_app
from app.core.database import sync_session_factory
from app.models import ModelConfig, Project, Report

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="report.generate", max_retries=0, time_limit=600)
def generate_report_summary(self: Any, report_id: int, project_id: int) -> dict[str, Any]:
    """异步撰写报告结论摘要。"""
    session = sync_session_factory()
    try:
        report = session.get(Report, report_id)
        project = session.get(Project, project_id)
        if report is None or project is None:
            raise RuntimeError("报告或项目不存在")

        model_config = session.get(ModelConfig, project.model_config_id) if project.model_config_id else None
        if model_config is None:
            raise RuntimeError("项目未绑定模型")

        summary_agent = SummaryAgent(model_config)
        summary = summary_agent.run(report.score, report.risk_level, report.top_issues or [])
        record_usage(
            session, project_id, model_config.id, "summary",
            summary_agent.usage.input_tokens, summary_agent.usage.output_tokens,
            task_type="report", task_id=report_id,
        )

        report.summary = summary
        report.status = "completed"
        session.commit()
        return {"report_id": report_id}

    except Exception:
        logger.exception("报告生成失败 report_id=%s", report_id)
        session.rollback()
        report = session.get(Report, report_id)
        if report is not None:
            report.status = "failed"
        session.commit()
        raise
    finally:
        session.close()
