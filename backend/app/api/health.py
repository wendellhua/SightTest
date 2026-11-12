"""健康检查接口。"""

from typing import Any

from fastapi import APIRouter

from app.core.response import ok

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, Any]:
    """服务存活探针。"""
    return ok({"status": "up"})
