"""统一响应结构。

成功与失败统一为 `{code, message, data}`，对齐《04.API接口设计.md》。
"""

from typing import Any

from app.core.exceptions import ErrorCode


def ok(data: Any = None, message: str = "ok") -> dict[str, Any]:
    """成功响应。"""
    return {"code": ErrorCode.OK, "message": message, "data": data}


def fail(code: ErrorCode, message: str, data: Any = None) -> dict[str, Any]:
    """失败响应。"""
    return {"code": int(code), "message": message, "data": data}
