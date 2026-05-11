# AGENTS.md

## 项目：RAG 个人网站

三合一个人网站：作品集 + 技术博客 + AI 知识库（RAG）。

## 架构

- `frontend/` — Vue 3 + Vite + TypeScript + Tailwind CSS + Pinia + Vue Router 4
- `backend/` — Python FastAPI + SQLAlchemy + MySQL（开发默认 MySQL，配置 DATABASE_URL 可切换）
- API 代理：Vite `/api` → `http://localhost:8000`

## 启动命令

### 前端（端口 3000）
```bash
cd frontend && npm run dev
npm run build    # 生产构建
npm run preview  # 预览
```

### 后端（端口 8000）
```bash
cd backend && uvicorn main:app --reload --port 8000
cd backend && pip install -e .  # 安装依赖
```

API 文档：
- Swagger UI（可交互调试）：http://localhost:8000/api/docs
- ReDoc：http://localhost:8000/api/redoc

**注意**：后端需要 Python >= 3.14。`package.json` 无 `lint`、`test`、`typecheck` 脚本。

## 已知问题

### 主题切换 Bug
`stores/theme.ts` 在 `<html>` 上添加/移除 `light` class，但 Tailwind `darkMode: 'class'` 需要 `dark` class 才能触发深色样式。当前深色模式不生效。修复方向：store 应切换 `dark` class 而非 `light`。

### 前端 Views 使用 Mock 数据
`BlogView.vue` 和 `ProjectsView.vue` 目前使用硬编码的本地数据，未调用后端 API。前端 API 层（`api/index.ts`）已就绪，需替换 mock 数据为真实 API 调用。

## 文件布局

```
frontend/src/
├── api/          — Axios 封装，blogApi / projectApi / ragApi
├── components/   — NavBar.vue, FooterBar.vue
├── composables/  — useSEO.ts
├── router/       — 8 条路由
├── stores/       — theme.ts
└── views/        — 8 个页面组件

backend/
├── main.py                        — FastAPI 入口，注册中间件/异常处理器/路由/lifespan
├── routers/                       — blog.py, project.py, rag.py, health.py
├── services/                      — 业务逻辑层，ORM → Schema 转换
├── models/                        — SQLAlchemy ORM 实体（BlogModel, ProjectModel）
├── schemas/                       — Pydantic v2 请求/响应 Schema
│   ├── blog.py, project.py, rag.py
│   ├── common.py                  — PaginationParams, PaginatedResult[T]
│   └── enums.py                   — BlogTag 枚举（10 个标签）
├── core/
│   ├── config.py                  — 加载 .env（含 DATABASE_URL，默认 MySQL）
│   ├── exception_handlers.py      — 全局异常 → Result.fail 转换器
│   └── logging_config.py          — 结构化控制台日志
├── utils/
│   ├── result.py                  — 统一响应 Result[T]
│   └── exceptions.py              — AppException / NotFoundException / ConflictException 等
├── database/                      — engine.py, session.py, base.py（SQLAlchemy 连接管理）
└── crud/                          — blog.py, project.py（SQLAlchemy 2.0 select 风格）
```

## API 端点

所有端点统一使用 `Result[T]` 响应格式：
```json
{"success": true, "data": T, "total": null, "errorMsg": null, "errCode": null}
```

| 方法 | 路径 | 查询参数 | 描述 |
|------|------|----------|------|
| GET | `/api/health` | — | 健康检查 |
| GET | `/api/blogs` | `page, page_size, search, tag` | 博客列表（分页 + 搜索 + 标签过滤） |
| GET | `/api/blogs/{slug}` | — | 博客详情（自动 +1 浏览量） |
| POST | `/api/blogs` | — | 创建博客（tags 受 BlogTag 枚举约束） |
| PUT | `/api/blogs/{slug}` | — | 更新博客（部分更新） |
| DELETE | `/api/blogs/{slug}` | — | 删除博客 |
| GET | `/api/projects` | `page, page_size, search, status, tech` | 项目列表（分页 + 搜索 + 过滤） |
| GET | `/api/projects/{id}` | — | 项目详情 |
| POST | `/api/projects` | — | 创建项目 |
| PUT | `/api/projects/{id}` | — | 更新项目（部分更新） |
| DELETE | `/api/projects/{id}` | — | 删除项目 |

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

## 关键约束

- **数据库**：SQLAlchemy ORM + MySQL（开发），配置 `DATABASE_URL` 可切换
- **分层架构**：`Router → Service → CRUD → ORM Model → Database`
- **CRUD 风格**：SQLAlchemy 2.0 `select()` 语句，非旧版 `session.query()`
- **统一响应**：所有 API 返回 `Result[T]` 格式
- **异常处理**：全局异常处理器将 AppException / RequestValidationError / IntegrityError 统一转为 Result.fail()
- **日志**：启动时自动初始化，格式 `[时间] [模块] [级别] 消息`
- **无安全**：CORS `allow_origins=["*"]`，无认证中间件
- **`@` 别名**：解析到 `frontend/src/`
