"""健康检查接口。"""

from fastapi import APIRouter

from app.core.response import ok

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    """服务存活探针。"""
    return ok({"status": "up"})
