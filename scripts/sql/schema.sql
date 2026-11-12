-- ============================================================================
-- Web 端智能测试系统 · 数据库建表脚本
-- 数据库：PostgreSQL 16
-- 约定：
--   · snake_case 命名，表名单数（users 为避开保留字 user 的例外）
--   · 自增主键 id BIGSERIAL
--   · 不使用物理外键，表间通过 xx_id 逻辑关联，由应用层维护完整性
--   · 时间统一 TIMESTAMPTZ（UTC 存储，展示层转换）
--   · 敏感信息加密存储，结构化/多值内容使用 JSONB
-- 依据：docs/design/03.数据库设计.md
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. users 用户
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id                       BIGSERIAL PRIMARY KEY,
    email                    VARCHAR(255) NOT NULL,
    password_hash            VARCHAR(255) NOT NULL,
    name                     VARCHAR(100) NOT NULL,
    is_admin                 BOOLEAN      NOT NULL DEFAULT FALSE,
    admin_password_changed   BOOLEAN      NOT NULL DEFAULT FALSE,
    status                   VARCHAR(20)  NOT NULL DEFAULT 'normal',
    cancellation_requested_at TIMESTAMPTZ NULL,
    created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at               TIMESTAMPTZ NOT NULL DEFAULT now()
);
COMMENT ON TABLE  users IS '用户（含内置 admin，注销冷静期状态）';
COMMENT ON COLUMN users.status IS '账号状态：normal 正常 / frozen 冻结(禁用) / cancelling 冷静期 / cancelled 已注销';
COMMENT ON COLUMN users.is_admin IS '是否内置平台管理员';
COMMENT ON COLUMN users.admin_password_changed IS 'admin 首次登录是否已改密';
COMMENT ON COLUMN users.cancellation_requested_at IS '注销申请时间（冷静期起点，空表示未申请注销）';
CREATE UNIQUE INDEX IF NOT EXISTS uq_users_email ON users (email);

-- ---------------------------------------------------------------------------
-- 2. email_verifications 邮箱验证码
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS email_verifications (
    id         BIGSERIAL PRIMARY KEY,
    email      VARCHAR(255) NOT NULL,
    code       VARCHAR(16)  NOT NULL,
    purpose    VARCHAR(20)  NOT NULL,
    expires_at TIMESTAMPTZ  NOT NULL,
    used       BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
);
COMMENT ON TABLE  email_verifications IS '注册 / 找回密码的邮箱验证码';
COMMENT ON COLUMN email_verifications.purpose IS '用途：register 注册 / reset_password 找回密码';
CREATE INDEX IF NOT EXISTS idx_email_verifications_lookup
    ON email_verifications (email, purpose, used);

-- ---------------------------------------------------------------------------
-- 3. model_configs 模型配置收集表
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS model_configs (
    id                BIGSERIAL PRIMARY KEY,
    user_id           BIGINT       NOT NULL,
    name              VARCHAR(100) NOT NULL,
    base_url          VARCHAR(500) NOT NULL,
    api_key_encrypted TEXT         NOT NULL,
    model             VARCHAR(100) NOT NULL DEFAULT 'gpt-4o',
    status            VARCHAR(20)  NOT NULL DEFAULT 'unverified',
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ  NOT NULL DEFAULT now()
);
COMMENT ON TABLE  model_configs IS '模型配置收集表（归属用户）';
COMMENT ON COLUMN model_configs.user_id IS '归属用户（逻辑关联 users.id）';
COMMENT ON COLUMN model_configs.api_key_encrypted IS 'API Key 密文（应用层加密）';
COMMENT ON COLUMN model_configs.model IS '模型名称（OpenAI 兼容的 model 参数，如 gpt-4o）';
COMMENT ON COLUMN model_configs.status IS '检测状态：verified 通过 / unverified 未通过';
CREATE INDEX IF NOT EXISTS idx_model_configs_user ON model_configs (user_id);

-- ---------------------------------------------------------------------------
-- 4. projects 项目
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS projects (
    id               BIGSERIAL PRIMARY KEY,
    name             VARCHAR(100) NOT NULL,
    url              VARCHAR(500) NOT NULL,
    creator_id       BIGINT       NOT NULL,
    model_config_id  BIGINT       NULL,
    plan_status      VARCHAR(20)  NOT NULL DEFAULT 'empty',
    plan_incomplete  BOOLEAN      NOT NULL DEFAULT FALSE,
    active_discovery BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT now()
);
COMMENT ON TABLE  projects IS '项目（被测网站）';
COMMENT ON COLUMN projects.creator_id IS '创建者（逻辑关联 users.id）';
COMMENT ON COLUMN projects.model_config_id IS '绑定模型（逻辑关联 model_configs.id，空项目为 NULL）';
COMMENT ON COLUMN projects.plan_status IS '方案状态：empty 无方案 / building 建设中 / ready 已就绪 / build_failed 建设失败';
COMMENT ON COLUMN projects.plan_incomplete IS '当前方案探索是否未完整';
COMMENT ON COLUMN projects.active_discovery IS '主动发现开关';
CREATE INDEX IF NOT EXISTS idx_projects_creator ON projects (creator_id);
CREATE INDEX IF NOT EXISTS idx_projects_model ON projects (model_config_id);

-- ---------------------------------------------------------------------------
-- 5. test_accounts 测试账号
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS test_accounts (
    id                     BIGSERIAL PRIMARY KEY,
    project_id             BIGINT       NOT NULL,
    username               VARCHAR(255) NOT NULL,
    password_encrypted     TEXT         NOT NULL,
    is_primary             BOOLEAN      NOT NULL DEFAULT FALSE,
    last_login_status      VARCHAR(20)  NULL,
    last_login_fail_reason VARCHAR(500) NULL,
    last_login_at          TIMESTAMPTZ  NULL,
    created_at             TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at             TIMESTAMPTZ  NOT NULL DEFAULT now()
);
COMMENT ON TABLE  test_accounts IS '项目测试账号（每个项目至少 1 个）';
COMMENT ON COLUMN test_accounts.project_id IS '所属项目（逻辑关联 projects.id）';
COMMENT ON COLUMN test_accounts.password_encrypted IS '账号密码密文（应用层加密）';
COMMENT ON COLUMN test_accounts.is_primary IS '是否主账号（每个项目仅一个主账号）';
COMMENT ON COLUMN test_accounts.last_login_status IS '最近登录结果：ok / fail / unused';
CREATE INDEX IF NOT EXISTS idx_test_accounts_project ON test_accounts (project_id);

-- ---------------------------------------------------------------------------
-- 6. plan_versions 方案版本
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS plan_versions (
    id              BIGSERIAL PRIMARY KEY,
    project_id      BIGINT      NOT NULL,
    version_no      INT         NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'building',
    plan_incomplete BOOLEAN     NOT NULL DEFAULT FALSE,
    explore_data    JSONB       NULL,
    explore_stats   JSONB       NULL,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at    TIMESTAMPTZ NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
COMMENT ON TABLE  plan_versions IS '方案版本（项目内最多保留 10 个）';
COMMENT ON COLUMN plan_versions.project_id IS '所属项目（逻辑关联 projects.id）';
COMMENT ON COLUMN plan_versions.version_no IS '版本号（项目内递增，与 project_id 联合唯一）';
COMMENT ON COLUMN plan_versions.status IS '状态：building 建设中 / completed 已完成 / failed 失败';
COMMENT ON COLUMN plan_versions.explore_data IS '探索原始数据（技术架构/HTML/JS/网络请求引用等结构化内容）';
COMMENT ON COLUMN plan_versions.explore_stats IS '探索统计（页面/功能/接口数、时长）';
CREATE INDEX IF NOT EXISTS idx_plan_versions_project ON plan_versions (project_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_plan_versions_no ON plan_versions (project_id, version_no);

-- ---------------------------------------------------------------------------
-- 7. cases 测试用例
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cases (
    id              BIGSERIAL PRIMARY KEY,
    project_id      BIGINT       NOT NULL,
    plan_version_id BIGINT       NOT NULL,
    case_type       VARCHAR(20)  NOT NULL,
    module_path     VARCHAR(500) NULL,
    page            VARCHAR(500) NULL,
    name            VARCHAR(255) NOT NULL,
    priority        VARCHAR(10)  NOT NULL DEFAULT 'P2',
    precondition    TEXT         NULL,
    steps           TEXT         NOT NULL,
    expect          TEXT         NOT NULL,
    automatable     BOOLEAN      NOT NULL DEFAULT TRUE,
    result          VARCHAR(20)  NOT NULL DEFAULT 'none',
    remark          VARCHAR(255) NULL,
    flags           JSONB        NULL,
    extension       JSONB        NULL,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
);
COMMENT ON TABLE  cases IS '测试用例（功能/接口/性能/机制四类）';
COMMENT ON COLUMN cases.project_id IS '所属项目（逻辑关联 projects.id）';
COMMENT ON COLUMN cases.plan_version_id IS '所属方案版本（逻辑关联 plan_versions.id）';
COMMENT ON COLUMN cases.case_type IS '用例类型：func 功能 / api 接口 / perf 性能 / mech 网站机制';
COMMENT ON COLUMN cases.module_path IS '功能模块路径（多级，如 商城/订单/下单）';
COMMENT ON COLUMN cases.priority IS '优先级：P0 / P1 / P2 / P3';
COMMENT ON COLUMN cases.automatable IS '是否可自动化';
COMMENT ON COLUMN cases.result IS '最近一次正式执行结果：none 未执行 / pass 通过 / fail 不通过 / blocked 阻塞';
COMMENT ON COLUMN cases.remark IS '备注（如「已失效」）';
COMMENT ON COLUMN cases.flags IS '标记：人工修改 / 人工新增 / 已自动修复（结构化 JSON）';
COMMENT ON COLUMN cases.extension IS '分类扩展字段（按 case_type，见需求 A-3）';
CREATE INDEX IF NOT EXISTS idx_cases_project ON cases (project_id);
CREATE INDEX IF NOT EXISTS idx_cases_plan_version ON cases (plan_version_id);
CREATE INDEX IF NOT EXISTS idx_cases_type ON cases (case_type);

-- ---------------------------------------------------------------------------
-- 8. executions 测试执行任务
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS executions (
    id              BIGSERIAL PRIMARY KEY,
    project_id      BIGINT       NOT NULL,
    plan_version_id BIGINT       NULL,
    plan_version_no INT          NOT NULL,
    name            VARCHAR(100) NOT NULL,
    scope           VARCHAR(20)  NOT NULL,
    is_debug        BOOLEAN      NOT NULL DEFAULT FALSE,
    status          VARCHAR(20)  NOT NULL DEFAULT 'queued',
    progress        INT          NOT NULL DEFAULT 0,
    order_items     JSONB        NULL,
    summary         JSONB        NULL,
    started_at      TIMESTAMPTZ  NULL,
    finished_at     TIMESTAMPTZ  NULL,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
);
COMMENT ON TABLE  executions IS '测试执行任务';
COMMENT ON COLUMN executions.project_id IS '所属项目（逻辑关联 projects.id）';
COMMENT ON COLUMN executions.plan_version_id IS '关联方案版本（逻辑关联 plan_versions.id；版本删除后置 NULL）';
COMMENT ON COLUMN executions.plan_version_no IS '方案版本号快照（保留历史，版本删除后仍可追溯）';
COMMENT ON COLUMN executions.scope IS '执行范围：full 全量 / func / api / perf / mech';
COMMENT ON COLUMN executions.is_debug IS '是否调试执行（true 为调试，不计入正式历史统计）';
COMMENT ON COLUMN executions.status IS '状态：queued 排队 / running 运行 / completed 完成 / failed 失败 / terminated 已终止';
COMMENT ON COLUMN executions.progress IS '进度百分比 0-100';
COMMENT ON COLUMN executions.order_items IS '执行顺序（结构化 JSON）';
COMMENT ON COLUMN executions.summary IS '通过/不通过/阻塞/未执行统计（结构化 JSON）';
CREATE INDEX IF NOT EXISTS idx_executions_project_status ON executions (project_id, status);
CREATE INDEX IF NOT EXISTS idx_executions_plan_version ON executions (plan_version_id);

-- ---------------------------------------------------------------------------
-- 9. case_executions 用例执行记录
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS case_executions (
    id              BIGSERIAL PRIMARY KEY,
    case_id         BIGINT      NOT NULL,
    execution_id    BIGINT      NOT NULL,
    plan_version_id BIGINT      NULL,
    result          VARCHAR(20) NOT NULL,
    evidence        JSONB       NULL,
    case_snapshot   JSONB       NULL,
    started_at      TIMESTAMPTZ NULL,
    finished_at     TIMESTAMPTZ NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
COMMENT ON TABLE  case_executions IS '用例级执行记录（历史结果 + 证据）';
COMMENT ON COLUMN case_executions.case_id IS '用例（逻辑关联 cases.id）';
COMMENT ON COLUMN case_executions.execution_id IS '所属任务（逻辑关联 executions.id）';
COMMENT ON COLUMN case_executions.plan_version_id IS '方案版本快照（逻辑关联 plan_versions.id，版本删除后置 NULL）';
COMMENT ON COLUMN case_executions.result IS '结果：pass / fail / blocked';
COMMENT ON COLUMN case_executions.evidence IS '证据引用（截图/请求响应/控制台报错，MinIO 引用）';
COMMENT ON COLUMN case_executions.case_snapshot IS '用例快照（名称/步骤/预期/类型/优先级等；用例删除后历史可追溯）';
CREATE INDEX IF NOT EXISTS idx_case_executions_case ON case_executions (case_id);
CREATE INDEX IF NOT EXISTS idx_case_executions_execution ON case_executions (execution_id);

-- ---------------------------------------------------------------------------
-- 10. issues 主动发现的问题
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS issues (
    id            BIGSERIAL PRIMARY KEY,
    project_id    BIGINT       NOT NULL,
    execution_id  BIGINT       NOT NULL,
    page          VARCHAR(500) NOT NULL,
    severity      VARCHAR(10)  NOT NULL,
    description   TEXT         NOT NULL,
    status        VARCHAR(20)  NOT NULL DEFAULT 'open',
    screenshot_ref TEXT        NULL,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);
COMMENT ON TABLE  issues IS '主动发现的问题（UI 执行中 Agent 主动判定）';
COMMENT ON COLUMN issues.project_id IS '所属项目（逻辑关联 projects.id）';
COMMENT ON COLUMN issues.execution_id IS '发现于哪次执行（逻辑关联 executions.id）';
COMMENT ON COLUMN issues.page IS '页面（结构相同视为同一页）';
COMMENT ON COLUMN issues.severity IS '严重程度：serious 严重 / normal 一般 / hint 提示';
COMMENT ON COLUMN issues.status IS '状态：open 正常 / misreported 误报';
COMMENT ON COLUMN issues.screenshot_ref IS '截图引用（MinIO）';
CREATE INDEX IF NOT EXISTS idx_issues_project ON issues (project_id);
CREATE INDEX IF NOT EXISTS idx_issues_execution ON issues (execution_id);
CREATE INDEX IF NOT EXISTS idx_issues_page ON issues (project_id, page);

-- ---------------------------------------------------------------------------
-- 11. issue_cases 问题-用例关联（多对多）
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS issue_cases (
    id       BIGSERIAL PRIMARY KEY,
    issue_id BIGINT NOT NULL,
    case_id  BIGINT NOT NULL
);
COMMENT ON TABLE  issue_cases IS '主动发现的问题与涉及用例的多对多关联';
COMMENT ON COLUMN issue_cases.issue_id IS '问题（逻辑关联 issues.id）';
COMMENT ON COLUMN issue_cases.case_id IS '用例（逻辑关联 cases.id）';
CREATE UNIQUE INDEX IF NOT EXISTS uq_issue_cases ON issue_cases (issue_id, case_id);
CREATE INDEX IF NOT EXISTS idx_issue_cases_case ON issue_cases (case_id);

-- ---------------------------------------------------------------------------
-- 12. misreport_patterns 误报忽略清单
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS misreport_patterns (
    id          BIGSERIAL PRIMARY KEY,
    project_id  BIGINT       NOT NULL,
    page        VARCHAR(500) NOT NULL,
    description TEXT         NOT NULL,
    status      VARCHAR(20)  NOT NULL DEFAULT 'active',
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);
COMMENT ON TABLE  misreport_patterns IS '误报忽略清单（后续执行中按页面+问题特征自动忽略）';
COMMENT ON COLUMN misreport_patterns.project_id IS '所属项目（逻辑关联 projects.id）';
COMMENT ON COLUMN misreport_patterns.page IS '页面匹配';
COMMENT ON COLUMN misreport_patterns.description IS '问题特征匹配规则';
COMMENT ON COLUMN misreport_patterns.status IS '状态：active 生效 / revoked 已撤销';
CREATE INDEX IF NOT EXISTS idx_misreport_patterns_project ON misreport_patterns (project_id, status);

-- ---------------------------------------------------------------------------
-- 13. reports 测试报告
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reports (
    id           BIGSERIAL PRIMARY KEY,
    project_id   BIGINT      NOT NULL,
    scope        VARCHAR(20) NOT NULL,
    execution_id BIGINT      NULL,
    status       VARCHAR(20) NOT NULL DEFAULT 'generating',
    score        INT         NOT NULL,
    risk_level   VARCHAR(10) NOT NULL,
    top_issues   JSONB       NULL,
    summary      TEXT        NULL,
    content_ref  TEXT        NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
COMMENT ON TABLE  reports IS '测试报告';
COMMENT ON COLUMN reports.project_id IS '所属项目（逻辑关联 projects.id）';
COMMENT ON COLUMN reports.scope IS '范围：execution 某次执行 / snapshot 项目当前状态';
COMMENT ON COLUMN reports.execution_id IS 'scope=execution 时关联任务（逻辑关联 executions.id）';
COMMENT ON COLUMN reports.status IS '生成状态：generating 生成中 / completed 完成 / failed 失败';
COMMENT ON COLUMN reports.score IS '综合评分 0-100';
COMMENT ON COLUMN reports.risk_level IS '风险等级：high / medium / low';
COMMENT ON COLUMN reports.top_issues IS '主要问题前几名（结构化 JSON）';
COMMENT ON COLUMN reports.summary IS '结论摘要（报告摘要 Agent 撰写）';
COMMENT ON COLUMN reports.content_ref IS '报告正文 / PDF 引用（MinIO）';
CREATE INDEX IF NOT EXISTS idx_reports_project ON reports (project_id);

-- ---------------------------------------------------------------------------
-- 14. platform_settings 平台设置（单行）
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS platform_settings (
    id                            SMALLINT PRIMARY KEY,
    total_concurrency             INT  NOT NULL DEFAULT 5,
    global_stress_limit           INT  NOT NULL DEFAULT 100,
    new_user_stress_limit         INT  NOT NULL DEFAULT 50,
    default_explore_minutes       INT  NOT NULL DEFAULT 60,
    default_explore_pages         INT  NOT NULL DEFAULT 200,
    retention_days                INT  NOT NULL DEFAULT 90,
    stress_duration_seconds       INT  NOT NULL DEFAULT 60,
    account_limit                 INT  NOT NULL DEFAULT 10,
    default_account_stress_limit  INT  NOT NULL DEFAULT 10,
    disclaimer                    TEXT NULL,
    updated_at                    TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_platform_settings_single CHECK (id = 1)
);
COMMENT ON TABLE  platform_settings IS '平台设置（单行，id 固定为 1）';
COMMENT ON COLUMN platform_settings.total_concurrency IS '平台总并发任务数';
COMMENT ON COLUMN platform_settings.global_stress_limit IS '单接口压测全局并发上限';
COMMENT ON COLUMN platform_settings.new_user_stress_limit IS '新用户压测并发上限';
COMMENT ON COLUMN platform_settings.default_explore_minutes IS '新用户探索时长上限（分钟）';
COMMENT ON COLUMN platform_settings.default_explore_pages IS '新用户探索页面数上限';
COMMENT ON COLUMN platform_settings.retention_days IS '大文件保留时长（天）';
COMMENT ON COLUMN platform_settings.stress_duration_seconds IS '压测默认持续时长（秒）';
COMMENT ON COLUMN platform_settings.account_limit IS '每项目测试账号上限';
COMMENT ON COLUMN platform_settings.default_account_stress_limit IS '新用户单账号压测并发上限';
COMMENT ON COLUMN platform_settings.disclaimer IS '免责声明内容';

-- ---------------------------------------------------------------------------
-- 15. user_settings 用户设置
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_settings (
    id                   BIGSERIAL PRIMARY KEY,
    user_id              BIGINT      NOT NULL,
    explore_minutes      INT         NOT NULL DEFAULT 60,
    explore_pages        INT         NOT NULL DEFAULT 200,
    stress_limit         INT         NOT NULL DEFAULT 50,
    account_stress_limit INT         NOT NULL DEFAULT 10,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);
COMMENT ON TABLE  user_settings IS '用户设置（探索限制、压测上限，每个用户一行）';
COMMENT ON COLUMN user_settings.user_id IS '归属用户（逻辑关联 users.id，一对一）';
COMMENT ON COLUMN user_settings.explore_minutes IS '探索时长上限（分钟）';
COMMENT ON COLUMN user_settings.explore_pages IS '探索页面数上限';
COMMENT ON COLUMN user_settings.stress_limit IS '单接口压测并发上限';
COMMENT ON COLUMN user_settings.account_stress_limit IS '单账号压测并发上限';
CREATE UNIQUE INDEX IF NOT EXISTS uq_user_settings_user ON user_settings (user_id);

-- ---------------------------------------------------------------------------
-- 16. model_call_logs 模型调用计量
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS model_call_logs (
    id              BIGSERIAL PRIMARY KEY,
    project_id      BIGINT      NULL,
    model_config_id BIGINT      NULL,
    agent           VARCHAR(50) NOT NULL,
    task_type       VARCHAR(20) NULL,
    task_id         BIGINT      NULL,
    input_tokens    INT         NOT NULL DEFAULT 0,
    output_tokens   INT         NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
COMMENT ON TABLE  model_call_logs IS '模型调用计量（token 用量，用于成本控制与主动发现开关判断）';
COMMENT ON COLUMN model_call_logs.project_id IS '关联项目（逻辑关联 projects.id，模型检测等非项目调用为 NULL）';
COMMENT ON COLUMN model_call_logs.model_config_id IS '使用的模型配置（逻辑关联 model_configs.id）';
COMMENT ON COLUMN model_call_logs.agent IS '调用来源 Agent（login/explore/analyze/...）';
COMMENT ON COLUMN model_call_logs.task_type IS '所属任务类型：build/execution/debug/report';
COMMENT ON COLUMN model_call_logs.task_id IS '所属任务 ID（逻辑关联对应任务表主键）';
COMMENT ON COLUMN model_call_logs.input_tokens IS '输入 token 数';
COMMENT ON COLUMN model_call_logs.output_tokens IS '输出 token 数';
CREATE INDEX IF NOT EXISTS idx_model_call_logs_project ON model_call_logs (project_id);
CREATE INDEX IF NOT EXISTS idx_model_call_logs_model ON model_call_logs (model_config_id);
CREATE INDEX IF NOT EXISTS idx_model_call_logs_task ON model_call_logs (task_type, task_id);

-- ============================================================================
-- 说明：
--   1. 不创建任何 FOREIGN KEY 约束，表间关系由应用层校验维护（遵循数据库设计规范）。
--   2. 删除策略（项目级联删除、版本删除保留历史等）由应用层实现，详见设计文档 §4.2。
--   3. 首次部署需 INSERT 单行 platform_settings（id=1），其余字段用默认值即可。
-- ============================================================================
