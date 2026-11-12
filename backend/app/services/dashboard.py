"""平台首页与项目仪表盘服务。"""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Case, Execution, Issue, Project
from app.services.project import get_owned_project

CASE_TYPES = ["func", "api", "perf", "mech"]


async def get_platform_home(db: AsyncSession, user_id: int) -> dict[str, Any]:
    """平台首页：项目数 + 能力介绍（能力介绍为静态，由前端渲染）。"""
    project_count = (
        await db.execute(select(func.count()).select_from(Project).where(Project.creator_id == user_id))
    ).scalar_one()
    return {"project_count": project_count}


async def get_project_dashboard(db: AsyncSession, user_id: int, project_id: int, is_admin: bool) -> dict[str, Any]:
    """项目仪表盘：测试状态总览。"""
    project = await get_owned_project(db, user_id, project_id, is_admin)

    cases = list((await db.execute(select(Case).where(Case.project_id == project_id))).scalars().all())
    case_stats = {ct: {"total": 0, "pass": 0, "fail": 0, "blocked": 0, "none": 0} for ct in CASE_TYPES}
    for c in cases:
        stat = case_stats.setdefault(c.case_type, {"total": 0, "pass": 0, "fail": 0, "blocked": 0, "none": 0})
        stat["total"] += 1
        key = c.result if c.result in ("pass", "fail", "blocked") else "none"
        stat[key] += 1

    open_issues = (
        await db.execute(
            select(func.count()).select_from(Issue).where(Issue.project_id == project_id, Issue.status == "open")
        )
    ).scalar_one()
    misreported = (
        await db.execute(
            select(func.count())
            .select_from(Issue)
            .where(Issue.project_id == project_id, Issue.status == "misreported")
        )
    ).scalar_one()

    running = list(
        (
            await db.execute(
                select(Execution).where(
                    Execution.project_id == project_id,
                    Execution.status.in_(["queued", "running"]),
                    Execution.is_debug.is_(False),
                )
            )
        ).scalars().all()
    )

    return {
        "plan_status": project.plan_status,
        "active_discovery": project.active_discovery,
        "run_status": "running" if running else "idle",
        "case_stats": case_stats,
        "issue_stats": {"open": open_issues, "misreported": misreported},
        "running_tasks": [{"id": e.id, "name": e.name, "progress": e.progress} for e in running],
    }
