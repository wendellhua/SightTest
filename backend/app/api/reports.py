"""报告路由。"""

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.response import ok
from app.models import User
from app.schemas.report import ReportCreate, ReportOut
from app.services import report as report_service

router = APIRouter(prefix="/projects/{project_id}/reports", tags=["reports"])


@router.post("")
async def create_report(
    project_id: int,
    data: ReportCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    report_id = await report_service.create_report(db, user.id, project_id, user.is_admin, data)
    return ok({"report_id": report_id})


@router.get("")
async def list_reports(
    project_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    total, items = await report_service.list_reports(db, user.id, project_id, user.is_admin, page, page_size)
    return ok(
        {
            "items": [ReportOut.model_validate(r) for r in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.get("/{report_id}")
async def get_report(
    project_id: int,
    report_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    report = await report_service.get_report(db, user.id, project_id, report_id, user.is_admin)
    return ok(ReportOut.model_validate(report))


@router.get("/{report_id}/pdf")
async def get_report_pdf(
    project_id: int,
    report_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    report = await report_service.get_report(db, user.id, project_id, report_id, user.is_admin)
    # TODO(阶段 7 迭代): 接入 PDF 库生成正式 PDF，当前返回报告文本
    content = (
        f"测试报告 #{report.id}\n"
        f"综合评分：{report.score}\n"
        f"风险等级：{report.risk_level}\n"
        f"结论摘要：{report.summary or '生成中'}\n"
    )
    return Response(
        content=content,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=report_{report.id}.txt"},
    )
