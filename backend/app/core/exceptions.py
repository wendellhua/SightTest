"""统一错误码与业务异常。

错误码取值对齐《04.API接口设计.md》错误码表。
"""

from enum import IntEnum


class ErrorCode(IntEnum):
    """业务错误码，稳定、可识别。"""

    OK = 0
    VALIDATION_ERROR = 40001
    UNAUTHORIZED = 40101
    INVALID_TOKEN = 40102
    FORBIDDEN = 40301
    NOT_FOUND = 40401
    CONFLICT = 40901
    TOO_MANY_REQUESTS = 42901
    INTERNAL_ERROR = 50001


# 错误码对应的 HTTP 状态码
_HTTP_STATUS: dict[ErrorCode, int] = {
    ErrorCode.OK: 200,
    ErrorCode.VALIDATION_ERROR: 400,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.INVALID_TOKEN: 401,
    ErrorCode.FORBIDDEN: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.CONFLICT: 409,
    ErrorCode.TOO_MANY_REQUESTS: 429,
    ErrorCode.INTERNAL_ERROR: 500,
}


class AppException(Exception):
    """业务异常，携带可识别错误码与用户可读信息。"""

    def __init__(self, code: ErrorCode, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)

    @property
    def http_status(self) -> int:
        return _HTTP_STATUS.get(self.code, 400)
