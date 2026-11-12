"""用量与成本统计服务（M11）。"""

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ModelCallLog, ModelConfig, Project
from app.utils.pricing import calc_cost

TASK_TYPE_TEXT = {"build": "方案建设", "execution": "测试执行", "debug": "调试执行", "report": "报告生成"}


def _task_name(task_type: str | None, task_id: int | None) -> str:
    text = TASK_TYPE_TEXT.get(task_type or "", task_type or "其他")
    if task_id:
        return f"{text} #{task_id}"
    return text


async def get_usage(db: AsyncSession, user_id: int, project_id: int | None, days: int) -> dict[str, Any]:
    """汇总当前用户自己项目的用量与成本（按项目/模型/任务三维度）。"""
    project_filters = [Project.creator_id == user_id]
    if project_id is not None:
        project_filters.append(Project.id == project_id)

    projects = (await db.execute(select(Project.id, Project.name).where(*project_filters))).all()
    project_id_to_name = dict(projects)
    project_ids = list(project_id_to_name.keys())

    overview = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_cost": 0.0,
        "cost_unknown": False,
        "project_count": len(project_ids),
    }
    if not project_ids:
        return {"overview": overview, "by_project": [], "by_model": [], "by_task": []}

    since = datetime.now(UTC) - timedelta(days=days)
    rows = (
        await db.execute(
            select(
                ModelCallLog.project_id,
                ModelCallLog.task_type,
                ModelCallLog.task_id,
                ModelCallLog.input_tokens,
                ModelCallLog.output_tokens,
                ModelConfig.model,
            )
            .outerjoin(ModelConfig, ModelConfig.id == ModelCallLog.model_config_id)
            .where(ModelCallLog.project_id.in_(project_ids), ModelCallLog.created_at >= since)
        )
    ).all()

    by_project: dict[int, dict[str, Any]] = {}
    by_model: dict[str, dict[str, Any]] = {}
    by_task: dict[tuple[Any, ...], dict[str, Any]] = {}

    for pid, task_type, task_id, in_tok, out_tok, model_name in rows:
        if pid is None:
            continue
        cost = calc_cost(model_name, in_tok, out_tok)

        overview["input_tokens"] += in_tok
        overview["output_tokens"] += out_tok
        if cost is not None:
            overview["total_cost"] = round(overview["total_cost"] + cost, 2)
        else:
            overview["cost_unknown"] = True

        p = by_project.setdefault(
            pid,
            {"project_id": pid, "project_name": project_id_to_name.get(pid, ""), "input_tokens": 0, "output_tokens": 0, "cost": 0.0, "cost_unknown": False},
        )
        p["input_tokens"] += in_tok
        p["output_tokens"] += out_tok
        if cost is not None:
            p["cost"] = round(p["cost"] + cost, 2)
        else:
            p["cost_unknown"] = True

        model_key = model_name or "未知模型"
        m = by_model.setdefault(model_key, {"model": model_key, "input_tokens": 0, "output_tokens": 0, "cost": None})
        m["input_tokens"] += in_tok
        m["output_tokens"] += out_tok
        if cost is not None:
            m["cost"] = round((m["cost"] or 0) + cost, 2)

        tkey = (task_type or "other", task_id or 0)
        t = by_task.setdefault(
            tkey,
            {"task_type": task_type, "task_id": task_id, "name": _task_name(task_type, task_id), "input_tokens": 0, "output_tokens": 0, "cost": 0.0, "cost_unknown": False},
        )
        t["input_tokens"] += in_tok
        t["output_tokens"] += out_tok
        if cost is not None:
            t["cost"] = round(t["cost"] + cost, 2)
        else:
            t["cost_unknown"] = True

    return {
        "overview": overview,
        "by_project": sorted(by_project.values(), key=lambda x: -x["cost"]),
        "by_model": sorted(by_model.values(), key=lambda x: -(x["cost"] or 0)),
        "by_task": sorted(by_task.values(), key=lambda x: -x["cost"]),
    }
