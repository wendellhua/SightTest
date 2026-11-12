"""报告服务：生成、列表、详情与导出。"""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.exceptions import AppException, ErrorCode
from app.models import Case, CaseExecution, Execution, Issue, Report
from app.schemas.report import ReportCreate
from app.services.project import get_owned_project
from app.tasks.report import generate_report_summary
from app.utils.scoring import calculate_score


def _extract_case_results(case_executions: list[CaseExecution]) -> list[dict[str, Any]]:
    results = []
    for ce in case_executions:
        snapshot = ce.case_snapshot or {}
        results.append(
            {
                "case_type": snapshot.get("case_type", "func"),
                "priority": snapshot.get("priority", "P2"),
                "result": ce.result,
            }
        )
    return results


def _build_top_issues(case_executions: list[CaseExecution], issues: list[Issue]) -> list[dict[str, Any]]:
    top: list[dict[str, Any]] = []
    for ce in case_executions:
        if ce.result == "fail":
            snapshot = ce.case_snapshot or {}
            top.append({"type": "case", "name": snapshot.get("name", ""), "priority": snapshot.get("priority", "P2")})
    for issue in issues:
        top.append({"type": "issue", "description": issue.description, "severity": issue.severity})
    return top[:10]


async def _get_report(db: AsyncSession, project_id: int, report_id: int) -> Report:
    report = (
        await db.execute(select(Report).where(Report.id == report_id, Report.project_id == project_id))
    ).scalar_one_or_none()
    if report is None:
        raise AppException(ErrorCode.NOT_FOUND, "报告不存在")
    return report


async def create_report(
    db: AsyncSession, user_id: int, project_id: int, is_admin: bool, data: ReportCreate
) -> int:
    """生成报告：同步计算评分/风险等级，摘要 Agent 异步撰写。"""
    await get_owned_project(db, user_id, project_id, is_admin)

    if data.scope == "execution":
        if data.execution_id is None:
            raise AppException(ErrorCode.VALIDATION_ERROR, "按执行生成报告需指定 execution_id")
        execution = (
            await db.execute(
                select(Execution).where(Execution.id == data.execution_id, Execution.project_id == project_id)
            )
        ).scalar_one_or_none()
        if execution is None:
            raise AppException(ErrorCode.NOT_FOUND, "执行记录不存在")
        case_executions = list(
            (await db.execute(select(CaseExecution).where(CaseExecution.execution_id == data.execution_id))).scalars().all()
        )
        issues = list(
            (await db.execute(select(Issue).where(Issue.execution_id == data.execution_id))).scalars().all()
        )
    else:
        # 项目当前状态：每条用例取最近一次结果
        all_ce = list(
            (
                await db.execute(
                    select(CaseExecution)
                    .join(Case, Case.id == CaseExecution.case_id)
                    .where(Case.project_id == project_id)
                    .order_by(CaseExecution.id.desc())
                )
            ).scalars().all()
        )
        latest: dict[int, CaseExecution] = {}
        for ce in all_ce:
            if ce.case_id not in latest:
                latest[ce.case_id] = ce
        case_executions = list(latest.values())
        issues = list((await db.execute(select(Issue).where(Issue.project_id == project_id))).scalars().all())

    scoring = calculate_score(_extract_case_results(case_executions), [{"severity": i.severity} for i in issues])

    report = Report(
        project_id=project_id,
        scope=data.scope,
        execution_id=data.execution_id if data.scope == "execution" else None,
        status="generating",
        score=scoring["score"],
        risk_level=scoring["risk_level"],
        top_issues=_build_top_issues(case_executions, issues),
    )
    db.add(report)
    await db.flush()
    await db.commit()

    await run_in_threadpool(
        generate_report_summary.apply_async, args=[report.id, project_id], task_id=str(report.id)
    )
    return report.id


async def list_reports(
    db: AsyncSession, user_id: int, project_id: int, is_admin: bool, page: int, page_size: int
) -> tuple[int, list[Report]]:
    await get_owned_project(db, user_id, project_id, is_admin)
    total = (
        await db.execute(select(func.count()).select_from(Report).where(Report.project_id == project_id))
    ).scalar_one()
    stmt = (
        select(Report)
        .where(Report.project_id == project_id)
        .order_by(Report.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list((await db.execute(stmt)).scalars().all())
    return total, items


async def get_report(db: AsyncSession, user_id: int, project_id: int, report_id: int, is_admin: bool) -> Report:
    await get_owned_project(db, user_id, project_id, is_admin)
    return await _get_report(db, project_id, report_id)
