"""测试执行服务：发起、进度、终止、结果、问题与误报清单。"""

from datetime import UTC, datetime, timedelta
from typing import Any

from celery.result import AsyncResult
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.celery_app import celery_app
from app.core.exceptions import AppException, ErrorCode
from app.models import Case, CaseExecution, Execution, Issue, MisreportPattern, PlanVersion
from app.schemas.execution import ExecutionCreate, IssueUpdate, MisreportPatternUpdate
from app.services.project import get_owned_project
from app.tasks.execution import run_execution

CASE_TYPE_ORDER = {"func": 0, "api": 1, "perf": 2, "mech": 3}
SCOPE_TEXT = {"full": "全量", "func": "功能", "api": "接口", "perf": "性能", "mech": "机制"}


async def _get_current_version(db: AsyncSession, project_id: int) -> PlanVersion:
    version = (
        await db.execute(
            select(PlanVersion)
            .where(PlanVersion.project_id == project_id, PlanVersion.status == "completed")
            .order_by(PlanVersion.version_no.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if version is None:
        raise AppException(ErrorCode.CONFLICT, "请先完成方案建设")
    return version


async def _get_execution(db: AsyncSession, project_id: int, execution_id: int) -> Execution:
    execution = (
        await db.execute(
            select(Execution).where(Execution.id == execution_id, Execution.project_id == project_id)
        )
    ).scalar_one_or_none()
    if execution is None:
        raise AppException(ErrorCode.NOT_FOUND, "执行记录不存在")
    return execution


async def start_execution(
    db: AsyncSession, user_id: int, project_id: int, is_admin: bool, data: ExecutionCreate
) -> int:
    """发起执行，返回 execution_id。"""
    project = await get_owned_project(db, user_id, project_id, is_admin)
    if project.plan_status != "ready":
        raise AppException(ErrorCode.CONFLICT, "请先完成方案建设")

    active = (
        await db.execute(
            select(Execution.id).where(
                Execution.project_id == project_id,
                Execution.status.in_(["queued", "running"]),
                Execution.is_debug.is_(False),
            )
        )
    ).scalar_one_or_none()
    if active is not None:
        raise AppException(ErrorCode.CONFLICT, "项目已有正在执行的任务")

    version = await _get_current_version(db, project_id)

    query = select(Case).where(Case.project_id == project_id)
    if data.scope != "full":
        query = query.where(Case.case_type == data.scope)
    if data.case_ids:
        query = query.where(Case.id.in_(data.case_ids))
    cases = list((await db.execute(query)).scalars().all())
    if not cases:
        raise AppException(ErrorCode.CONFLICT, "没有可执行的用例")

    ordered = sorted(cases, key=lambda c: CASE_TYPE_ORDER.get(c.case_type, 99))
    execution = Execution(
        project_id=project_id,
        plan_version_id=version.id,
        plan_version_no=version.version_no,
        name=f"{SCOPE_TEXT.get(data.scope, data.scope)}执行",
        scope=data.scope,
        status="queued",
        order_items=[c.id for c in ordered],
    )
    db.add(execution)
    await db.flush()
    await db.commit()

    await run_in_threadpool(run_execution.apply_async, args=[execution.id, project_id], task_id=str(execution.id))
    return execution.id


async def list_executions(
    db: AsyncSession,
    user_id: int,
    project_id: int,
    is_admin: bool,
    include_debug: bool,
    page: int,
    page_size: int,
) -> tuple[int, list[Execution]]:
    await get_owned_project(db, user_id, project_id, is_admin)
    filters = [Execution.project_id == project_id]
    if not include_debug:
        filters.append(Execution.is_debug.is_(False))
    total = (await db.execute(select(func.count()).select_from(Execution).where(*filters))).scalar_one()
    stmt = (
        select(Execution)
        .where(*filters)
        .order_by(Execution.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list((await db.execute(stmt)).scalars().all())
    return total, items


async def get_execution(
    db: AsyncSession, user_id: int, project_id: int, execution_id: int, is_admin: bool
) -> Execution:
    await get_owned_project(db, user_id, project_id, is_admin)
    return await _get_execution(db, project_id, execution_id)


def _revoke(execution_id: int) -> None:
    AsyncResult(str(execution_id), app=celery_app).revoke(terminate=True)


async def terminate_execution(
    db: AsyncSession, user_id: int, project_id: int, execution_id: int, is_admin: bool
) -> None:
    await get_owned_project(db, user_id, project_id, is_admin)
    execution = await _get_execution(db, project_id, execution_id)
    if execution.status not in ("queued", "running"):
        raise AppException(ErrorCode.CONFLICT, "执行已结束，无法终止")

    await run_in_threadpool(_revoke, execution_id)
    execution.status = "terminated"
    execution.finished_at = datetime.now(UTC)
    await db.commit()


async def list_case_executions(
    db: AsyncSession,
    user_id: int,
    project_id: int,
    execution_id: int,
    is_admin: bool,
    result: str | None,
) -> list[CaseExecution]:
    await get_owned_project(db, user_id, project_id, is_admin)
    await _get_execution(db, project_id, execution_id)
    filters = [CaseExecution.execution_id == execution_id]
    if result:
        filters.append(CaseExecution.result == result)
    stmt = select(CaseExecution).where(*filters).order_by(CaseExecution.id)
    return list((await db.execute(stmt)).scalars().all())


async def list_issues(
    db: AsyncSession,
    user_id: int,
    project_id: int,
    is_admin: bool,
    severity: str | None,
    page: int,
    page_size: int,
) -> tuple[int, list[Issue]]:
    await get_owned_project(db, user_id, project_id, is_admin)
    filters = [Issue.project_id == project_id]
    if severity:
        filters.append(Issue.severity == severity)
    total = (await db.execute(select(func.count()).select_from(Issue).where(*filters))).scalar_one()
    stmt = select(Issue).where(*filters).order_by(Issue.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list((await db.execute(stmt)).scalars().all())
    return total, items


async def update_issue(
    db: AsyncSession, user_id: int, project_id: int, issue_id: int, is_admin: bool, data: IssueUpdate
) -> Issue:
    await get_owned_project(db, user_id, project_id, is_admin)
    issue = (
        await db.execute(select(Issue).where(Issue.id == issue_id, Issue.project_id == project_id))
    ).scalar_one_or_none()
    if issue is None:
        raise AppException(ErrorCode.NOT_FOUND, "问题不存在")

    issue.status = data.status
    if data.status == "misreported":
        db.add(MisreportPattern(project_id=project_id, page=issue.page, description=issue.description))

    await db.commit()
    await db.refresh(issue)
    return issue


async def list_misreport_patterns(
    db: AsyncSession, user_id: int, project_id: int, is_admin: bool
) -> list[MisreportPattern]:
    await get_owned_project(db, user_id, project_id, is_admin)
    stmt = select(MisreportPattern).where(MisreportPattern.project_id == project_id).order_by(MisreportPattern.id.desc())
    return list((await db.execute(stmt)).scalars().all())


async def update_misreport_pattern(
    db: AsyncSession, user_id: int, project_id: int, pattern_id: int, is_admin: bool, data: MisreportPatternUpdate
) -> MisreportPattern:
    await get_owned_project(db, user_id, project_id, is_admin)
    pattern = (
        await db.execute(
            select(MisreportPattern).where(MisreportPattern.id == pattern_id, MisreportPattern.project_id == project_id)
        )
    ).scalar_one_or_none()
    if pattern is None:
        raise AppException(ErrorCode.NOT_FOUND, "误报清单不存在")

    pattern.status = data.status
    await db.commit()
    await db.refresh(pattern)
    return pattern


async def get_perf_trends(
    db: AsyncSession, user_id: int, project_id: int, is_admin: bool, case_id: int, days: int
) -> list[dict[str, Any]]:
    await get_owned_project(db, user_id, project_id, is_admin)
    since = datetime.now(UTC) - timedelta(days=days)
    stmt = (
        select(CaseExecution)
        .where(CaseExecution.case_id == case_id, CaseExecution.finished_at >= since)
        .order_by(CaseExecution.finished_at.asc())
    )
    items = (await db.execute(stmt)).scalars().all()
    return [
        {"time": item.finished_at.isoformat() if item.finished_at else None, "result": item.result}
        for item in items
    ]
