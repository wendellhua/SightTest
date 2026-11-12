<div align="center">

# SightTest

**基于大模型 Agent 的 Web 端智能测试系统**

输入被测网站 URL 与测试账号，系统自动完成登录、自主探索、产品分析、测试用例生成，并执行功能 / 接口 / 性能 / 机制四类测试，最终产出「结论先行」的测试报告与用量成本统计。

*让测试从「人工编写用例」走向「Agent 自动生成 + 代码自动执行」。*

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.x-4FC08D?logo=vue.js)](https://vuejs.org/)

</div>

---

## ✨ 核心能力

| 能力 | 说明 |
|---|---|
| 🤖 自动方案建设 | 登录 Agent 自动登录（含验证码识别），探索 Agent 自主遍历站点，产品分析 + 用例生成，产出结构化测试方案 |
| 🧪 四类测试 | 功能（UI 操作）、接口（正常 + 变异 + 越权）、性能（页面加载 + 接口压测）、网站机制（SEO / 分享卡片等） |
| ⚡ 真实执行 | Playwright 真实浏览器 + 代码级接口 / 压测执行，结果可复现、可追溯 |
| 🐛 主动发现问题 | 执行过程中 Agent 主动发现用例断言之外的问题，支持误报标记 |
| 📊 结论先行报告 | 评分（0–100）、风险等级（高 / 中 / 低）、主要问题、结论摘要，一键导出 |
| 💰 用量与成本 | 任务维度 token 消耗量与资金成本（元）实时统计，按项目 / 任务 / 模型三维汇总 |
| 🔐 多账号与权限 | 多测试账号交叉压测、项目数据归属、admin 后台管理 |

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Vue 3 前端（SPA）                      │
└───────────────────────────┬─────────────────────────────────┘
                            │ REST /api/v1（JWT）
┌───────────────────────────▼─────────────────────────────────┐
│                    FastAPI 后端（async）                      │
│  api → services → models（SQLAlchemy）                       │
│            └─ agents（LangChain，11 个单一职责 Agent）        │
│            └─ runner（Playwright / 接口 / 压测引擎）          │
│            └─ tasks（Celery 异步长任务 + 进度）              │
└──────┬──────────────────────┬──────────────────────┬────────┘
       │                      │                      │
  PostgreSQL              Redis (broker)          MinIO
  （业务数据）            （任务队列/结果）        （截图/证据/PDF）
```

**技术栈**

| 层 | 技术 |
|---|---|
| 后端 | FastAPI · SQLAlchemy 2.x（async）· Celery · LangChain · LangChain-OpenAI · Playwright |
| 存储 | PostgreSQL 16 · Redis 7 · MinIO |
| 前端 | Vue 3 · TypeScript · Element Plus · Pinia · Vue Router · Vite |

## 🧠 Agent 编排

系统将大模型能力封装为 **11 个单一职责 Agent**，仅在「生成 / 判定 / 修复 / 摘要」环节调用；执行阶段尽量由代码完成，保证结果可复现：

`登录` · `探索` · `产品分析` · `功能用例生成` · `UI 脚本` · `接口用例生成` · `性能用例生成` · `网站机制评估` · `版本比对` · `UI 判定` · `报告摘要`

每次调用通过 LangChain 回调自动计量 token，落库 `model_call_logs`，用于用量成本统计与主动发现开关。

## 📦 功能模块

账号认证 · 项目管理 · 模型配置 · 方案建设 · 测试资产（用例）· 测试执行 · 测试报告 · 仪表盘 · 用户设置 · admin 后台 · 用量与成本

## 🚀 快速开始

### 前置要求

- Python 3.12+、Node.js 18+
- Docker（运行 PostgreSQL / Redis / MinIO）

### 1. 启动依赖中间件

```bash
docker compose -f deploy/docker-compose.yml up -d
```

### 2. 启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env               # 填写 ENCRYPTION_KEY、JWT_SECRET_KEY 等

# 初始化数据库（权威表结构 + Alembic 基线）
psql -h localhost -U sighttest -d sighttest -f ../scripts/sql/schema.sql
alembic upgrade head

# 启动 API
uvicorn app.main:app --reload --port 8000
```

### 3. 启动 Celery Worker（另开终端）

```bash
cd backend
celery -A worker.celery_app worker --loglevel=info
```

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 5. 安装浏览器（方案建设 / 功能执行需要）

```bash
playwright install chromium
```

访问前端进入系统，流程：**注册登录 → 创建项目 → 绑定模型 → 方案建设 → 用例管理 → 测试执行 → 报告 → 用量与成本**。

### 注册与邮箱验证码（开发环境）

验证码通过邮件发送，**接口响应中不包含验证码**。开发环境可使用内置的 MailPit 本地邮件服务器收信：

1. 启动依赖中间件（含 MailPit）：`docker compose -f deploy/docker-compose.yml up -d`
2. 在后端 `.env` 中配置：

   ```env
   SMTP_HOST=localhost
   SMTP_PORT=1025
   SMTP_START_TLS=false
   ```

3. 点击「发送验证码」后，打开 MailPit Web UI（http://localhost:8025）查看邮件并复制验证码

生产环境请配置真实的 `SMTP_*` 环境变量，验证码将通过真实邮件服务发送。

### 默认管理员账号

系统首次启动时会自动创建内置管理员账号（幂等，已存在则跳过），可直接登录体验后台管理：

| 邮箱 | 密码 |
|---|---|
| `admin@st.com` | `admin123` |

> 首次登录后建议立即修改密码。默认账号密码可通过后端 `.env` 中的 `ADMIN_EMAIL`、`ADMIN_PASSWORD` 环境变量自定义。

## 📁 目录结构

```
SightTest/
├── backend/               # FastAPI 后端
│   ├── app/
│   │   ├── agents/        # LangChain Agent（能力层 + 计量）
│   │   ├── api/           # REST 路由（按模块分包）
│   │   ├── core/          # 配置 / 数据库 / 异常 / 安全 / 日志
│   │   ├── models/        # ORM 模型（零物理外键）
│   │   ├── runner/        # 执行引擎（Playwright 浏览器等）
│   │   ├── schemas/       # Pydantic 请求 / 响应模型
│   │   ├── services/      # 领域服务（事务边界）
│   │   ├── tasks/         # Celery 异步任务
│   │   └── utils/         # 工具（邮件 / 模型检测 / 评分 / 价格表）
│   ├── alembic/           # 数据库迁移
│   ├── worker.py          # Celery Worker 入口
│   └── pyproject.toml     # 依赖与工具链配置
├── frontend/              # Vue 3 前端
├── deploy/                # docker-compose（PostgreSQL / Redis / MinIO）
├── scripts/sql/           # 建表脚本（schema.sql）
└── prototype/             # 页面原型（静态）
```

## 🔌 接口一览

共 61 个 REST 接口，覆盖 11 个功能模块；统一响应结构 `{code, message, data}`，JWT Bearer 鉴权，长任务（方案建设 / 执行 / 报告）走 Celery 异步 + 轮询。详细定义见各模块路由 `backend/app/api/`。

## 🤝 贡献

欢迎提交 Issue 与 Pull Request。提交前请确保 `ruff` 与 `mypy` 检查通过（`pip install -e ".[dev]"` 已含工具链）。

## 📄 License

[MIT](LICENSE) © 2026 wendellhua
