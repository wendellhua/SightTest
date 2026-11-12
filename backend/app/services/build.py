"""方案建设服务：启动、进度、终止、版本管理。"""

from datetime import UTC, datetime

from celery.result import AsyncResult
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.celery_app import celery_app
from app.core.exceptions import AppException, ErrorCode
from app.models import Case, Execution, PlanVersion
from app.schemas.build import BuildOut, BuildStartRequest
from app.services.project import get_owned_project
from app.tasks.build import run_build

MAX_VERSIONS = 10


async def _get_plan_version(db: AsyncSession, project_id: int, build_id: int) -> PlanVersion:
    version = (
        await db.execute(select(PlanVersion).where(PlanVersion.id == build_id, PlanVersion.project_id == project_id))
    ).scalar_one_or_none()
    if version is None:
        raise AppException(ErrorCode.NOT_FOUND, "建设记录不存在")
    return version


async def _trim_versions(db: AsyncSession, project_id: int) -> None:
    """控制版本数量：超出上限时删除最旧的版本（保留历史执行结果）。"""
    versions = (
        await db.execute(
            select(PlanVersion)
            .where(PlanVersion.project_id == project_id)
            .order_by(PlanVersion.version_no.desc())
        )
    ).scalars().all()
    if len(versions) < MAX_VERSIONS:
        return
    for version in versions[MAX_VERSIONS - 1:]:
        await db.execute(update(Execution).where(Execution.plan_version_id == version.id).values(plan_version_id=None))
        await db.execute(delete(Case).where(Case.plan_version_id == version.id))
        await db.execute(delete(PlanVersion).where(PlanVersion.id == version.id))
    await db.commit()


async def start_build(
    db: AsyncSession, user_id: int, project_id: int, is_admin: bool, data: BuildStartRequest
) -> int:
    """启动方案建设/重新探索，返回 build_id（即 plan_version.id）。"""
    project = await get_owned_project(db, user_id, project_id, is_admin)
    if project.model_config_id is None:
        raise AppException(ErrorCode.CONFLICT, "请先绑定模型配置")

    building = (
        await db.execute(
            select(PlanVersion.id).where(PlanVersion.project_id == project_id, PlanVersion.status == "building")
        )
    ).scalar_one_or_none()
    if building is not None:
        raise AppException(ErrorCode.CONFLICT, "项目已有正在进行的方案建设")

    max_no = (
        await db.execute(select(func.max(PlanVersion.version_no)).where(PlanVersion.project_id == project_id))
    ).scalar_one()
    version_no = (max_no or 0) + 1

    await _trim_versions(db, project_id)

    plan_version = PlanVersion(
        project_id=project_id,
        version_no=version_no,
        status="building",
        started_at=datetime.now(UTC),
    )
    db.add(plan_version)
    await db.flush()
    project.plan_status = "building"
    await db.commit()

    await run_in_threadpool(
        run_build.apply_async, args=[plan_version.id, project_id], task_id=str(plan_version.id)
    )
    return plan_version.id


def _read_progress(build_id: int) -> tuple[str | None, int]:
    result = AsyncResult(str(build_id), app=celery_app)
    if result.state == "PROGRESS" and result.info:
        return result.info.get("stage"), result.info.get("progress", 0)
    return None, 0


async def get_build(
    db: AsyncSession, user_id: int, project_id: int, build_id: int, is_admin: bool
) -> BuildOut:
    """查询建设进度。"""
    await get_owned_project(db, user_id, project_id, is_admin)
    plan_version = await _get_plan_version(db, project_id, build_id)

    stage: str | None = None
    progress = 0
    if plan_version.status == "building":
        stage, progress = await run_in_threadpool(_read_progress, build_id)

    return BuildOut(
        build_id=plan_version.id,
        project_id=plan_version.project_id,
        status=plan_version.status,
        stage=stage,
        progress=progress,
        plan_incomplete=plan_version.plan_incomplete,
    )


def _revoke(build_id: int) -> None:
    AsyncResult(str(build_id), app=celery_app).revoke(terminate=True)


async def terminate_build(
    db: AsyncSession, user_id: int, project_id: int, build_id: int, is_admin: bool
) -> None:
    """终止建设。"""
    project = await get_owned_project(db, user_id, project_id, is_admin)
    plan_version = await _get_plan_version(db, project_id, build_id)
    if plan_version.status != "building":
        raise AppException(ErrorCode.CONFLICT, "建设已结束，无法终止")

    await run_in_threadpool(_revoke, build_id)
    plan_version.status = "terminated"
    plan_version.plan_incomplete = True
    project.plan_status = "build_failed"
    await db.commit()


async def list_versions(db: AsyncSession, user_id: int, project_id: int, is_admin: bool) -> list[PlanVersion]:
    """方案版本列表。"""
    await get_owned_project(db, user_id, project_id, is_admin)
    stmt = select(PlanVersion).where(PlanVersion.project_id == project_id).order_by(PlanVersion.version_no.desc())
    return list((await db.execute(stmt)).scalars().all())


async def get_version(
    db: AsyncSession, user_id: int, project_id: int, version_id: int, is_admin: bool
) -> PlanVersion:
    """版本详情（含 explore_data 功能图）。"""
    await get_owned_project(db, user_id, project_id, is_admin)
    return await _get_plan_version(db, project_id, version_id)
