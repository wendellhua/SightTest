"""用例服务：CRUD 与调试执行入口。"""

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.exceptions import AppException, ErrorCode
from app.models import Case, Execution, PlanVersion
from app.schemas.case import CaseCreate, CaseUpdate
from app.services.project import get_owned_project
from app.tasks.debug import run_debug


async def _get_current_version(db: AsyncSession, project_id: int) -> PlanVersion:
    """获取当前已就绪的方案版本（最新 completed）。"""
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


async def _get_case(db: AsyncSession, project_id: int, case_id: int) -> Case:
    case = (
        await db.execute(select(Case).where(Case.id == case_id, Case.project_id == project_id))
    ).scalar_one_or_none()
    if case is None:
        raise AppException(ErrorCode.NOT_FOUND, "用例不存在")
    return case


async def list_cases(
    db: AsyncSession,
    user_id: int,
    project_id: int,
    is_admin: bool,
    case_type: str | None,
    version_id: int | None,
    page: int,
    page_size: int,
) -> tuple[int, list[Case]]:
    await get_owned_project(db, user_id, project_id, is_admin)
    filters = [Case.project_id == project_id]
    if case_type:
        filters.append(Case.case_type == case_type)
    if version_id:
        filters.append(Case.plan_version_id == version_id)

    total = (await db.execute(select(func.count()).select_from(Case).where(*filters))).scalar_one()
    stmt = select(Case).where(*filters).order_by(Case.id.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list((await db.execute(stmt)).scalars().all())
    return total, items


async def get_case(db: AsyncSession, user_id: int, project_id: int, case_id: int, is_admin: bool) -> Case:
    await get_owned_project(db, user_id, project_id, is_admin)
    return await _get_case(db, project_id, case_id)


async def create_case(
    db: AsyncSession, user_id: int, project_id: int, is_admin: bool, data: CaseCreate
) -> Case:
    await get_owned_project(db, user_id, project_id, is_admin)
    version = await _get_current_version(db, project_id)

    flags = dict(data.flags or {})
    flags["manual_added"] = True

    case = Case(
        project_id=project_id,
        plan_version_id=version.id,
        case_type=data.case_type,
        module_path=data.module_path,
        page=data.page,
        name=data.name,
        priority=data.priority,
        precondition=data.precondition,
        steps=data.steps,
        expect=data.expect,
        automatable=data.automatable,
        remark=data.remark,
        flags=flags,
        extension=data.extension,
    )
    db.add(case)
    await db.commit()
    await db.refresh(case)
    return case


async def update_case(
    db: AsyncSession, user_id: int, project_id: int, case_id: int, is_admin: bool, data: CaseUpdate
) -> Case:
    await get_owned_project(db, user_id, project_id, is_admin)
    case = await _get_case(db, project_id, case_id)

    payload = data.model_dump(exclude_unset=True)
    flags = dict(case.flags or {})
    for field, value in payload.items():
        if field != "flags":
            setattr(case, field, value)
    flags.update(payload.get("flags") or {})
    flags["manual_modified"] = True
    case.flags = flags

    await db.commit()
    await db.refresh(case)
    return case


async def delete_case(db: AsyncSession, user_id: int, project_id: int, case_id: int, is_admin: bool) -> None:
    await get_owned_project(db, user_id, project_id, is_admin)
    case = await _get_case(db, project_id, case_id)
    await db.execute(delete(Case).where(Case.id == case.id))
    await db.commit()


async def debug_case(db: AsyncSession, user_id: int, project_id: int, case_id: int, is_admin: bool) -> int:
    """调试执行：创建 is_debug=true 的 execution 并触发调试任务。"""
    await get_owned_project(db, user_id, project_id, is_admin)
    case = await _get_case(db, project_id, case_id)
    version = await _get_current_version(db, project_id)

    execution = Execution(
        project_id=project_id,
        plan_version_id=case.plan_version_id,
        plan_version_no=version.version_no,
        name=f"调试：{case.name}",
        scope="func",
        is_debug=True,
        status="queued",
    )
    db.add(execution)
    await db.flush()
    await db.commit()

    await run_in_threadpool(run_debug.apply_async, args=[execution.id, case.id], task_id=str(execution.id))
    return execution.id
