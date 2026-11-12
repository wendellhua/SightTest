# SightTest 后端

Web 端智能测试系统后端：FastAPI + SQLAlchemy 2.x + Celery + PostgreSQL + Redis + MinIO。

## 目录结构

```
backend/
├── app/
│   ├── main.py          # FastAPI 入口（中间件、异常处理、路由装配）
│   ├── core/            # 配置、数据库、异常、响应、安全、日志
│   ├── api/             # REST 路由（按模块分包）
│   ├── services/        # 领域服务（事务边界）
│   ├── models/          # ORM 模型（无物理外键）
│   ├── schemas/         # Pydantic 请求/响应模型
│   ├── agents/          # LangChain Agent（能力层）
│   ├── runner/          # 执行引擎（Playwright/压测/whistle）
│   └── tasks/           # Celery 任务
├── alembic/             # 数据库迁移
├── pyproject.toml       # 依赖与工具配置
└── .env.example         # 环境变量示例
```

## 快速启动

1. 创建虚拟环境并安装依赖：

   ```bash
   python -m venv .venv
   .venv\Scripts\activate          # Windows
   pip install -e ".[dev]"
   ```

2. 配置环境变量：

   ```bash
   copy .env.example .env
   # 编辑 .env：至少设置 ENCRYPTION_KEY 与 JWT_SECRET_KEY
   # ENCRYPTION_KEY 生成：python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

3. 启动依赖中间件：

   ```bash
   docker compose -f ../deploy/docker-compose.yml up -d
   ```

4. 初始化数据库（权威表结构）：

   ```bash
   psql -h localhost -U sighttest -d sighttest -f ../scripts/sql/schema.sql
   alembic upgrade head        # 建立 Alembic 基线
   ```

5. 启动 API 服务：

   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   访问健康检查：`GET http://localhost:8000/health`；开发调试文档：设置 `DEBUG=true` 后访问 `/docs`。

6. 启动 Celery Worker（另开终端，Windows 下默认 threads pool）：

   ```bash
   celery -A worker.celery_app worker --loglevel=info
   ```

   方案建设、测试执行等长任务均在 Worker 中异步执行。

## 表结构变更

- 初始表结构以 `scripts/sql/schema.sql` 为准，Alembic 基线为 `0001`。
- 后续任何表结构变更一律通过 Alembic：`alembic revision --autogenerate -m "描述"` 后 `alembic upgrade head`。
