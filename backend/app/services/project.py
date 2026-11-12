"""项目与测试账号服务。

项目归属、数量上限、URL 检测、级联删除（无物理外键，应用层维护）均在此层处理。
"""

import httpx
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException, ErrorCode
from app.core.security import encrypt_secret
from app.models import (
    Case,
    CaseExecution,
    Execution,
    Issue,
    IssueCase,
    MisreportPattern,
    ModelCallLog,
    PlanVersion,
    PlatformSetting,
    Project,
    Report,
    TestAccount,
)
from app.schemas.project import AccountIn, AccountUpdate, ProjectCreate, ProjectUpdate

MAX_PROJECTS = 10
DEFAULT_ACCOUNT_LIMIT = 10


async def check_url(url: str) -> bool:
    """检测被测网站 URL 是否可达。"""
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url)
            return resp.status_code < 400
    except httpx.HTTPError:
        return False


async def _account_limit(db: AsyncSession) -> int:
    setting = (await db.execute(select(PlatformSetting).where(PlatformSetting.id == 1))).scalar_one_or_none()
    return setting.account_limit if setting else DEFAULT_ACCOUNT_LIMIT


async def get_owned_project(db: AsyncSession, user_id: int, project_id: int, is_admin: bool) -> Project:
    project = (await db.execute(select(Project).where(Project.id == project_id))).scalar_one_or_none()
    if project is None:
        raise AppException(ErrorCode.NOT_FOUND, "项目不存在")
    if not is_admin and project.creator_id != user_id:
        raise AppException(ErrorCode.FORBIDDEN, "无权操作该项目")
    return project


async def create_project(db: AsyncSession, user_id: int, data: ProjectCreate) -> Project:
    count = (
        await db.execute(select(func.count()).select_from(Project).where(Project.creator_id == user_id))
    ).scalar_one()
    if count >= MAX_PROJECTS:
        raise AppException(ErrorCode.CONFLICT, f"项目数量已达上限（{MAX_PROJECTS} 个）")

    if not await check_url(data.url):
        raise AppException(ErrorCode.CONFLICT, "被测网站 URL 不可访问，请检查地址")

    project = Project(
        name=data.name,
        url=data.url,
        creator_id=user_id,
        model_config_id=data.model_config_id,
    )
    db.add(project)
    await db.flush()

    explicit_primary = next((a for a in data.accounts if a.is_primary), None)
    for index, acc in enumerate(data.accounts):
        is_primary = acc is explicit_primary or (explicit_primary is None and index == 0)
        db.add(
            TestAccount(
                project_id=project.id,
                username=acc.username,
                password_encrypted=encrypt_secret(acc.password),
                is_primary=is_primary,
            )
        )

    await db.commit()
    await db.refresh(project)
    return project


async def list_projects(db: AsyncSession, user_id: int, page: int, page_size: int) -> tuple[int, list[Project]]:
    total = (
        await db.execute(select(func.count()).select_from(Project).where(Project.creator_id == user_id))
    ).scalar_one()
    stmt = (
        select(Project)
        .where(Project.creator_id == user_id)
        .order_by(Project.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    projects = list((await db.execute(stmt)).scalars().all())
    return total, projects


async def get_project(db: AsyncSession, user_id: int, project_id: int, is_admin: bool) -> Project:
    return await get_owned_project(db, user_id, project_id, is_admin)


async def update_project(
    db: AsyncSession, user_id: int, project_id: int, is_admin: bool, data: ProjectUpdate
) -> Project:
    project = await get_owned_project(db, user_id, project_id, is_admin)
    payload = data.model_dump(exclude_unset=True)
    if payload.get("name") is not None:
        project.name = payload["name"]
    if "model_config_id" in payload:
        project.model_config_id = payload["model_config_id"]
    if payload.get("active_discovery") is not None:
        project.active_discovery = payload["active_discovery"]
    await db.commit()
    await db.refresh(project)
    return project


async def cascade_delete_project(db: AsyncSession, project_id: int) -> None:
    """物理级联删除项目及其全部关联数据（无物理外键，应用层维护）。"""
    exec_ids = select(Execution.id).where(Execution.project_id == project_id)
    case_ids = select(Case.id).where(Case.project_id == project_id)
    issue_ids = select(Issue.id).where(Issue.project_id == project_id)

    # 先删除无 project_id 的关联表（通过子查询定位）
    await db.execute(
        delete(CaseExecution).where(
            CaseExecution.execution_id.in_(exec_ids) | CaseExecution.case_id.in_(case_ids)
        )
    )
    await db.execute(delete(IssueCase).where(IssueCase.issue_id.in_(issue_ids)))

    await db.execute(delete(Issue).where(Issue.project_id == project_id))
    await db.execute(delete(Execution).where(Execution.project_id == project_id))
    await db.execute(delete(Case).where(Case.project_id == project_id))
    await db.execute(delete(PlanVersion).where(PlanVersion.project_id == project_id))
    await db.execute(delete(TestAccount).where(TestAccount.project_id == project_id))
    await db.execute(delete(MisreportPattern).where(MisreportPattern.project_id == project_id))
    await db.execute(delete(Report).where(Report.project_id == project_id))
    await db.execute(delete(ModelCallLog).where(ModelCallLog.project_id == project_id))
    await db.execute(delete(Project).where(Project.id == project_id))
    await db.commit()


async def delete_project(db: AsyncSession, user_id: int, project_id: int, is_admin: bool) -> None:
    await get_owned_project(db, user_id, project_id, is_admin)
    await cascade_delete_project(db, project_id)


async def list_accounts(db: AsyncSession, user_id: int, project_id: int, is_admin: bool) -> list[TestAccount]:
    await get_owned_project(db, user_id, project_id, is_admin)
    stmt = select(TestAccount).where(TestAccount.project_id == project_id).order_by(TestAccount.id)
    return list((await db.execute(stmt)).scalars().all())


async def add_account(
    db: AsyncSession, user_id: int, project_id: int, is_admin: bool, data: AccountIn
) -> TestAccount:
    await get_owned_project(db, user_id, project_id, is_admin)
    count = (
        await db.execute(select(func.count()).select_from(TestAccount).where(TestAccount.project_id == project_id))
    ).scalar_one()
    if count >= await _account_limit(db):
        raise AppException(ErrorCode.CONFLICT, "测试账号数量已达上限")

    if data.is_primary:
        await db.execute(update(TestAccount).where(TestAccount.project_id == project_id).values(is_primary=False))

    account = TestAccount(
        project_id=project_id,
        username=data.username,
        password_encrypted=encrypt_secret(data.password),
        is_primary=data.is_primary,
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


async def update_account(
    db: AsyncSession, user_id: int, project_id: int, account_id: int, is_admin: bool, data: AccountUpdate
) -> TestAccount:
    await get_owned_project(db, user_id, project_id, is_admin)
    account = (
        await db.execute(
            select(TestAccount).where(TestAccount.id == account_id, TestAccount.project_id == project_id)
        )
    ).scalar_one_or_none()
    if account is None:
        raise AppException(ErrorCode.NOT_FOUND, "测试账号不存在")

    payload = data.model_dump(exclude_unset=True)
    if payload.get("username") is not None:
        account.username = payload["username"]
    if payload.get("password") is not None:
        account.password_encrypted = encrypt_secret(payload["password"])
    if payload.get("is_primary") is True:
        await db.execute(
            update(TestAccount)
            .where(TestAccount.project_id == project_id, TestAccount.id != account_id)
            .values(is_primary=False)
        )
        account.is_primary = True

    await db.commit()
    await db.refresh(account)
    return account


async def delete_account(db: AsyncSession, user_id: int, project_id: int, account_id: int, is_admin: bool) -> None:
    await get_owned_project(db, user_id, project_id, is_admin)
    account = (
        await db.execute(
            select(TestAccount).where(TestAccount.id == account_id, TestAccount.project_id == project_id)
        )
    ).scalar_one_or_none()
    if account is None:
        raise AppException(ErrorCode.NOT_FOUND, "测试账号不存在")

    count = (
        await db.execute(select(func.count()).select_from(TestAccount).where(TestAccount.project_id == project_id))
    ).scalar_one()
    if count <= 1:
        raise AppException(ErrorCode.CONFLICT, "项目至少保留一个测试账号")

    await db.execute(delete(TestAccount).where(TestAccount.id == account_id))
    await db.commit()
