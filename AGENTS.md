# AGENTS.md

## 项目：RAG 个人网站

三合一个人网站：作品集 + 技术博客 + AI 知识库（RAG）。

## 架构

- `frontend/` — Vue 3 + Vite + TypeScript + Tailwind CSS + Pinia + Vue Router 4
- `backend/` — Python FastAPI + SQLAlchemy + MySQL（开发默认 MySQL，配置 DATABASE_URL 可切换）
- API 代理：Vite `/api` → `http://localhost:8000`

## 启动命令

### 前端（端口 5173）
```bash
cd frontend && npm run dev
npm run build    # 生产构建
npm run preview  # 预览
```

### 后端（端口 8000）
```bash
cd backend && uvicorn main:app --reload --port 8000
cd backend && pip install -e .  # 安装依赖（使用 pyproject.toml）
```

API 文档：
- Swagger UI（可交互调试）：http://localhost:8000/api/docs
- ReDoc：http://localhost:8000/api/redoc

**注意**：后端需要 Python >= 3.14。`package.json` 无 `lint`、`test`、`typecheck` 脚本。

## 已知问题

_当前无已知待修复问题。以下问题已解决：_
- ~~主题切换 Bug~~ — 已修复：`stores/theme.ts` 现在正确切换 `dark` class。
- ~~前端 Views 使用 Mock 数据~~ — 已修复：`BlogView.vue` 和 `ProjectsView.vue` 已接入真实 API。

## 项目文档

| 文件 | 描述 |
|------|------|
| `SPEC.md` | 项目规格文档（定位、设计规范、功能模块、API 设计、SEO 配置） |
| `docs/DEVELOPMENT.md` | 开发指南（环境要求、启动步骤、添加页面/组件/接口） |
| `docs/README.md` | 项目自述文件 |
| `AGENTS.md` | AI 编码助手指南（本文档） |

## 文件布局

```
frontend/src/
├── api/          — Axios 封装，blogApi / projectApi / awardApi / ragApi
├── assets/       — 静态资源（styles/ 全局样式）
├── components/   — NavBar.vue, FooterBar.vue, SkillRadar.vue
├── composables/  — useSEO.ts
├── router/       — 9 条路由（首页/博客/项目/关于/RAG/管理后台）
├── stores/       — theme.ts
├── utils/        — 工具函数（预留，当前为空）
└── views/        — 9 个页面组件

backend/
├── main.py                        — FastAPI 入口，注册中间件/异常处理器/路由/lifespan
├── routers/                       — blog.py, project.py, rag.py, health.py, award.py, admin.py, contact.py
├── services/                      — 业务逻辑层，ORM → Schema 转换
│   ├── blog_service.py, project_service.py, rag_service.py
│   └── award_service.py
├── models/                        — SQLAlchemy ORM 实体
│   ├── blog.py, project.py, award.py
│   └── contact.py
├── schemas/                       — Pydantic v2 请求/响应 Schema
│   ├── blog.py, project.py, rag.py, award.py
│   ├── contact.py
│   ├── common.py                  — PaginationParams, PaginatedResult[T]
│   └── enums.py                   — BlogTag 枚举（10 个标签）+ AwardLevel 枚举（9 个级别）
├── core/
│   ├── config.py                  — 加载 .env（含 DATABASE_URL，默认 MySQL）
│   ├── auth.py                    — JWT 创建/验证工具（python-jose）
│   ├── exception_handlers.py      — 全局异常 → Result.fail 转换器
│   └── logging_config.py          — 结构化控制台日志
├── utils/
│   ├── result.py                  — 统一响应 Result[T]
│   └── exceptions.py              — AppException / NotFoundException / ConflictException 等
├── database/                      — engine.py, session.py, base.py（SQLAlchemy 连接管理）
├── crud/                          — blog.py, project.py, award.py（SQLAlchemy 2.0 select 风格）
├── config/                        — 额外配置（预留，当前为空）
├── seed.py                        — 数据库种子脚本（Blog/Project/Award 示例数据）
├── .env                           — 环境变量（APP_NAME, DATABASE_URL, DEBUG, ADMIN_SECRET, ADMIN_TOKEN）
├── pyproject.toml                 — Python 项目配置与依赖
└── self_website.db                — 本地 SQLite 数据库文件（开发时可能存在，生产使用 MySQL）
```

## API 端点

所有端点统一使用 `Result[T]` 响应格式：
```json
{"success": true, "data": T, "total": null, "errorMsg": null, "errCode": null}
```

### 健康检查

| 方法 | 路径 | 查询参数 | 描述 |
|------|------|----------|------|
| GET | `/api/health` | — | 健康检查 |

### 博客（Blog）

| 方法 | 路径 | 查询参数 | 描述 |
|------|------|----------|------|
| GET | `/api/blogs` | `page, page_size, search, tag` | 博客列表（分页 + 搜索 + 标签过滤） |
| GET | `/api/blogs/{slug}` | — | 博客详情（自动 +1 浏览量） |
| POST | `/api/blogs` | — | 创建博客（tags 受 BlogTag 枚举约束） |
| PUT | `/api/blogs/{slug}` | — | 更新博客（部分更新） |
| DELETE | `/api/blogs/{slug}` | — | 删除博客 |

### 项目（Project）

| 方法 | 路径 | 查询参数 | 描述 |
|------|------|----------|------|
| GET | `/api/projects` | `page, page_size, search, status, tech` | 项目列表（分页 + 搜索 + 过滤） |
| GET | `/api/projects/{id}` | — | 项目详情 |
| POST | `/api/projects` | — | 创建项目 |
| PUT | `/api/projects/{id}` | — | 更新项目（部分更新） |
| DELETE | `/api/projects/{id}` | — | 删除项目 |

### 奖项（Award）

| 方法 | 路径 | 查询参数 | 描述 |
|------|------|----------|------|
| GET | `/api/awards` | `page, page_size, search, level` | 奖项列表（分页 + 搜索 + 级别过滤） |
| GET | `/api/awards/{award_id}` | — | 奖项详情 |
| POST | `/api/awards` | — | 创建奖项 |
| PUT | `/api/awards/{award_id}` | — | 更新奖项（部分更新） |
| DELETE | `/api/awards/{award_id}` | — | 删除奖项 |

### 联系表单（Contact）

| 方法 | 路径 | 查询参数 | 描述 |
|------|------|----------|------|
| POST | `/api/contact/` | — | 提交联系表单（公开，无需认证） |

### 管理后台（Admin）— JWT 保护

| 方法 | 路径 | 查询参数 | 描述 |
|------|------|----------|------|
| POST | `/api/admin/login` | — | 管理员登录（返回 JWT token） |
| POST | `/api/admin/blogs` | — | 创建博客 |
| PUT | `/api/admin/blogs/{slug}` | — | 更新博客 |
| DELETE | `/api/admin/blogs/{slug}` | — | 删除博客 |
| POST | `/api/admin/projects` | — | 创建项目 |
| PUT | `/api/admin/projects/{id}` | — | 更新项目 |
| DELETE | `/api/admin/projects/{id}` | — | 删除项目 |
| POST | `/api/admin/awards` | — | 创建奖项 |
| PUT | `/api/admin/awards/{id}` | — | 更新奖项 |
| DELETE | `/api/admin/awards/{id}` | — | 删除奖项 |
| GET | `/api/admin/contacts` | — | 查看所有联系表单提交 |

管理后台端点需 `Authorization: Bearer <token>` 头部。

RAG 端点（`/api/rag/*`）仅为桩代码，二期实现。

### 列表分页响应格式
```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 42,
    "page": 1,
    "page_size": 10,
    "total_pages": 5
  }
}
```

### BlogTag 枚举（10 个标签）

`前端` / `Vue` / `JavaScript` / `后端` / `Python` / `AI` / `DevOps` / `数据库` / `安全` / `架构`

定义于 `schemas/enums.py`，创建/更新博客时 tags 必须从此枚举中选择。

### AwardLevel 枚举（9 个级别）

`国家级` / `省级` / `市级` / `校级` / `一等奖` / `二等奖` / `三等奖` / `优秀奖` / `其他`

定义于 `schemas/enums.py`，创建/更新奖项时 level 必须从此枚举中选择。

## 关键约束

- **前端端口 3000 已占用**：端口 3000 由用户代理使用，**严禁**将 Vite dev server 或任何服务绑定到 3000 端口。Vite 默认 5173。
- **数据库**：SQLAlchemy ORM + MySQL（开发），配置 `DATABASE_URL` 可切换（.env 中默认 `mysql+pymysql://root:123456@localhost:3306/self_website`）
- **分层架构**：`Router → Service → CRUD → ORM Model → Database`
- **CRUD 风格**：SQLAlchemy 2.0 `select()` 语句，非旧版 `session.query()`
- **统一响应**：所有 API 返回 `Result[T]` 格式
- **异常处理**：全局异常处理器将 AppException / RequestValidationError / IntegrityError 统一转为 Result.fail()
- **日志**：启动时自动初始化，格式 `[时间] [模块] [级别] 消息`
- **安全**：公开端点无认证；管理后台（`/api/admin/*`）使用 JWT Bearer token（`core/auth.py`，python-jose HS256）
- **CORS**：`allow_origins=["*"]`
- **`@` 别名**：解析到 `frontend/src/`
