# RAG 个人网站

集**个人作品集** + **技术博客** + **AI 私有知识库（RAG）** 三合一的高端个人官网。

## 技术栈

| 层级 | 技术选型 |
|------|----------|
| 前端框架 | Vue 3 + Vite + TypeScript |
| UI 样式 | Tailwind CSS |
| 状态管理 | Pinia |
| 路由 | Vue Router 4 |
| 后端框架 | Python + FastAPI |
| 向量数据库 | Qdrant |
| RAG 模型 | DeepSeek-V4 + BGE-M3 + BGE-Reranker |
| LLM 框架 | LangChain |
| 评估框架 | RAGAS |
| Markdown 渲染 | marked |
| HTTP 客户端 | Axios |

## 项目结构

```
SelfWebsite/
├── frontend/                    # 前端项目
│   ├── public/                 # 静态资源
│   ├── src/
│   │   ├── api/               # API 请求封装
│   │   ├── assets/           # 资源文件
│   │   │   └── styles/       # 全局样式
│   │   ├── components/       # 公共组件
│   │   ├── composables/      # 组合式函数
│   │   ├── router/           # 路由配置
│   │   ├── stores/           # Pinia 状态管理
│   │   ├── utils/            # 工具函数
│   │   ├── views/            # 页面组件
│   │   ├── App.vue
│   │   └── main.ts
│   └── ...
│
├── backend/                    # 后端项目
│   ├── core/                  # 核心配置
│   ├── routers/               # API 路由
│   ├── schemas/               # 请求/响应 Schema
│   ├── services/             # 业务逻辑
│   ├── rag/                 # RAG 管线（ingest/query/rerank/eval）
│   ├── models/              # SQLAlchemy ORM
│   ├── database/            # 数据库连接
│   └── main.py
│
└── docs/                       # 开发文档
```

## 快速开始

### 前端

```bash
cd frontend
npm install
npm run dev
```



### 后端

```bash
cd backend
pip install -e .
uvicorn main:app --reload --port 8000
```


## 开发路线图

### Phase 1 
- [x] 官网首页
- [x] 技术博客展示
- [x] 个人作品集
- [x] 明暗主题切换
- [x] 响应式布局
- [x] RAG 入口预留

### Phase 2 (已完成)
- [x] RAG 问答系统（流式 + 非流式）
- [x] 知识库管理后台（JWT 保护）
- [x] DeepSeek-V4 集成（自动降级）
- [x] 多文档解析（PDF/Word/Markdown/TXT）
- [x] 向量数据库集成（Qdrant + BM25 混合检索）
- [x] RAGAS 评估（单条 + 批量）
- [x] 请求级全链路监控

## 页面列表

| 路径 | 描述 |
|------|------|
| / | 首页 |
| /blog | 博客列表 |
| /blog/:slug | 博客详情 |
| /projects | 作品集 |
| /projects/:id | 项目详情 |
| /about | 关于页面 |
| /rag | RAG 知识库入口 |
| /rag/chat | AI 智能对话（RAG 流式）|

## RAG 架构

```
用户提问 → Query 改写 → 多查询混合检索（BGE-M3 + BM25 + RRF）
         → BGE-Reranker 精排 → DeepSeek-V4 生成 → SSE 流式返回
```

## API 接口

### 博客
- `GET /api/blogs` - 获取博客列表
- `GET /api/blogs/:slug` - 获取博客详情

### 项目
- `GET /api/projects` - 获取项目列表
- `GET /api/projects/:id` - 获取项目详情

### RAG 公开接口
- `POST /api/rag/query` - 问答查询（非流式）
- `POST /api/rag/query/stream` - 问答查询（SSE 流式）
- `POST /api/rag/evaluate` - RAGAS 单条评估
- `GET /api/rag/knowledge-bases` - 知识库列表
- `GET /api/rag/conversations` - 对话记录（分页）
- `GET /api/health` - 健康检查

### 管理后台（JWT 保护）
- `POST /api/admin/login` - 管理员登录
- `GET /api/admin/rag/documents` - 文档列表（分页）
- `POST /api/admin/rag/documents` - 上传文档
- `DELETE /api/admin/rag/documents/{id}` - 删除文档
- `CRUD /api/admin/rag/knowledge-bases` - 知识库 CRUD
