# AGENTS.md

## 项目：RAG 个人网站

三合一个人网站：作品集 + 技术博客 + AI 知识库（RAG）。

## 架构

- `frontend/` — Vue 3 + Vite + TypeScript + Tailwind CSS + Pinia + Vue Router 4
- `backend/` — Python FastAPI + SQLAlchemy（默认 SQLite，配置 DATABASE_URL 可切换 MySQL）
- API 代理：Vite `/api` → `http://localhost:8000`

## 启动命令

### 前端（端口 3000）
```bash
cd frontend && npm run dev
npm run build    # 生产构建
npm run preview  # 预览
```

**注意**：`package.json` 无 `lint`、`test`、`typecheck` 脚本。

### 后端（端口 8000）
```bash
cd backend && uvicorn main:app --reload --port 8000
cd backend && pip install -e .  # 安装依赖（含 pydantic-settings）
```

API 文档：http://localhost:8000/docs

**注意**：后端需要 Python >= 3.14（来自 `pyproject.toml`）。

## 已知问题

### 主题切换 Bug
`stores/theme.ts` 在 `<html>` 上添加/移除 `light` class，但 Tailwind `darkMode: 'class'` 需要 `dark` class 才能触发深色样式。当前深色模式不生效。

修复方向：store 应切换 `dark` class 而非 `light`。

## 文件布局

```
frontend/src/
├── api/         — Axios 封装
├── components/  — NavBar.vue, FooterBar.vue
├── composables/ — useSEO.ts
├── router/      — 8 条路由
├── stores/      — theme.ts
└── views/       — 8 个页面组件

backend/
├── main.py
├── routers/     — blog.py, project.py, rag.py, health.py
├── services/    — 业务逻辑，直接操作 Pydantic schema
├── models/      — SQLAlchemy ORM 实体（BlogModel, ProjectModel）
├── schemas/     — 请求/响应 Schema（Pydantic v2）
├── core/        — config.py（加载 .env，含 DATABASE_URL）
├── utils/       — result.py（统一响应 Result[T]）
├── database/    — engine.py, session.py, base.py（SQLAlchemy 连接管理）
├── crud/        — blog.py, project.py（数据库 CRUD 操作）
├── config/      — （空占位）
└── self_website.db — SQLite 开发数据库（自动创建，git ignored）
```

## API 端点

所有端点统一使用 `Result[T]` 响应格式：
```json
{"success": true, "data": T, "total": null, "errorMsg": null, "errCode": null}
```

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/blogs` | 博客列表 |
| GET | `/api/blogs/{slug}` | 博客详情 |
| POST/PUT/DELETE | `/api/blogs/{slug}` | CRUD |
| GET | `/api/projects` | 项目列表 |
| GET | `/api/projects/{id}` | 项目详情 |

RAG 端点（`/api/rag/*`）仅为桩代码，二期实现。

## 视觉风格

- 玻璃拟态设计，深色基色 `#0a0a0f`
- 强调色：`#FE2C55` / `#25F4EE`（已在 SPEC.md 规划，尚未加入 Tailwind 配置）
- 自定义动画：`fade-in`, `slide-up`, `slide-down`, `scale-in`, `glow`

## 关键约束

- **数据库**：SQLAlchemy ORM + SQLite（开发），配置 `DATABASE_URL` 可切换 MySQL
- **分层架构**：`Router → Service → CRUD → ORM Model → Database`
- **统一响应**：所有 API 返回 `Result[T]` 格式（`utils/result.py`），错误时不抛 HTTPException 而是 `Result.fail()`
- **无安全**：CORS `allow_origins=["*"]`，无认证中间件
- **`@` 别名**：解析到 `frontend/src/`