"""FastAPI 应用入口：装配中间件、全局异常处理与路由。"""

import logging
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.api.builds import router as builds_router
from app.api.cases import router as cases_router
from app.api.dashboard import router as dashboard_router
from app.api.executions import router as executions_router
from app.api.health import router as health_router
from app.api.models import router as models_router
from app.api.projects import router as projects_router
from app.api.reports import router as reports_router
from app.api.settings import router as settings_router
from app.api.usage import router as usage_router
from app.api.users import router as users_router
from app.core.bootstrap import ensure_admin_user
from app.core.config import settings
from app.core.exceptions import AppException, ErrorCode
from app.core.logging import setup_logging

setup_logging(settings.debug)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """应用生命周期：启动时确保内置管理员账号存在。"""
    await ensure_admin_user()
    yield


app = FastAPI(
    title=settings.app_name,
    docs_url="/docs" if settings.debug else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def attach_request_id(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """为每个响应附加可追溯 ID（可选能力）。"""
    request_id = request.headers.get("X-Request-Id") or uuid.uuid4().hex
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.http_status,
        content={"code": int(exc.code), "message": exc.message, "data": None},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    fields = [
        {"field": ".".join(str(part) for part in err["loc"][1:]), "reason": err["msg"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=400,
        content={"code": int(ErrorCode.VALIDATION_ERROR), "message": "参数校验失败", "data": {"fields": fields}},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code_map = {401: ErrorCode.UNAUTHORIZED, 403: ErrorCode.FORBIDDEN, 404: ErrorCode.NOT_FOUND}
    code = code_map.get(exc.status_code, ErrorCode.INTERNAL_ERROR)
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": int(code), "message": str(exc.detail), "data": None},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("未处理异常：%s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"code": int(ErrorCode.INTERNAL_ERROR), "message": "服务器内部错误", "data": None},
    )


app.include_router(health_router)
app.include_router(dashboard_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(projects_router)
app.include_router(reports_router)
app.include_router(builds_router)
app.include_router(cases_router)
app.include_router(executions_router)
app.include_router(models_router)
app.include_router(settings_router)
app.include_router(usage_router)
app.include_router(admin_router)
