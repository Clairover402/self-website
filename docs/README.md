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

访问 http://localhost:3000

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API 文档：http://localhost:8000/docs

## 开发路线图

### Phase 1 (当前)
- [x] 官网首页
- [x] 技术博客展示
- [x] 个人作品集
- [x] 明暗主题切换
- [x] 响应式布局
- [x] RAG 入口预留

### Phase 2 (待开发)
- [ ] RAG 问答系统
- [ ] 知识库管理后台
- [ ] DeepSeek-V4 集成
- [ ] 多文档解析
- [ ] 向量数据库集成

## 页面列表

| 路径 | 描述 |
|------|------|
| / | 首页 |
| /blog | 博客列表 |
| /blog/:slug | 博客详情 |
| /projects | 作品集 |
| /projects/:id | 项目详情 |
| /about | 关于页面 |
| /rag | RAG 入口页（预留）|
| /rag/chat | AI 对话页（预留）|

## API 接口

### 博客
- `GET /api/blogs` - 获取博客列表
- `GET /api/blogs/:slug` - 获取博客详情

### 项目
- `GET /api/projects` - 获取项目列表
- `GET /api/projects/:id` - 获取项目详情

### RAG (预留)
- `POST /api/rag/query` - 问答查询
- `GET /api/rag/knowledge-bases` - 获取知识库列表
