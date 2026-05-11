# RAG 个人网站项目规划

## 1. 项目概述

### 1.1 项目定位
打造一款集**个人作品集** + **技术博客** + **AI 私有知识库（RAG）** 三合一的高端个人官网。

### 1.2 开发节奏
- **一期（当前）**：完成除 RAG 外的全站基础功能
- **二期（后续）**：接入 DeepSeek-V4 与全链路自建 RAG 能力

### 1.3 技术栈
| 层级 | 技术选型 |
|------|----------|
| 前端框架 | Vue 3 + Vite + TypeScript |
| UI 样式 | Tailwind CSS |
| 状态管理 | Pinia |
| 路由 | Vue Router 4 |
| 后端框架 | Python + FastAPI |
| Markdown 渲染 | marked |
| HTTP 客户端 | Axios |

---

## 2. 设计规范

### 2.1 视觉风格
- **主题**：玻璃拟态（Glassmorphism）+ 毛玻璃质感
- **基调**：科技深色主题
- **配色方案**：
  - 主色：深色背景（#0a0a0f 近似抖音深色）
  - 强调色：抖音红/科技蓝渐变（#FE2C55 / #25F4EE）
  - 毛玻璃：rgba(255,255,255,0.05) + backdrop-blur

### 2.2 动效规范
- 微交互时长：150-300ms
- 缓动函数：ease-out 进入，ease-in 退出
- 页面切换：淡入淡出 + 轻微上移
- 悬停反馈：scale(1.02) + 发光效果

### 2.3 响应式断点
| 设备 | 宽度 |
|------|------|
| 移动端 | < 640px |
| 平板 | 640px - 1024px |
| 桌面 | > 1024px |

---

## 3. 功能模块

### 3.1 一期功能（P0 + P1）

#### P0 - 基础核心
- [x] 官网首页
- [x] 路由架构（Vue Router）
- [x] 响应式布局
- [x] UI 视觉与动效骨架
- [x] 预留 RAG 入口页面

#### P1 - 一期必做
- [x] Markdown 技术博客展示
- [x] 个人项目作品集
- [x] 全站明暗主题切换
- [x] 基础页面导航与内容渲染

### 3.2 二期功能（P2 - 暂搁置）
- [ ] RAG 问答系统
- [ ] 知识库管理后台
- [ ] AI 聊天助手
- [ ] 多知识库分组
- [ ] 用户系统
- [ ] 数据统计
- [ ] 多语言支持

---

## 4. 页面结构

```
/
├── /                     # 首页
├── /blog                 # 博客列表
│   └── /blog/:slug       # 博客详情
├── /projects             # 作品集
│   └── /projects/:id     # 项目详情
├── /about                # 关于页
├── /rag                  # RAG 入口页（二期待开发）
│   └── /rag/chat         # AI 对话页（二期待开发）
└── /admin                # 管理后台入口（二期待开发）
```

---

## 5. API 接口设计

### 5.1 基础接口（已实现）
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/health | 健康检查 |
| GET | /api/blogs | 获取博客列表 |
| GET | /api/blogs/:slug | 获取博客详情 |
| GET | /api/projects | 获取项目列表 |
| GET | /api/projects/:id | 获取项目详情 |

### 5.2 RAG 接口（预留空位，二期实现）
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/rag/query | 问答查询 |
| GET | /api/rag/knowledge-bases | 获取知识库列表 |
| POST | /api/rag/knowledge-bases | 创建知识库 |
| DELETE | /api/rag/knowledge-bases/:id | 删除知识库 |
| POST | /api/rag/documents | 上传文档 |
| GET | /api/rag/documents | 获取文档列表 |

---

## 6. 项目目录结构

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
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── backend/                    # 后端项目
│   ├── core/                  # 核心配置
│   │   ├── config.py
│   │   └── security.py
│   ├── models/                # 数据模型（Pydantic）
│   ├── routers/               # API 路由
│   │   ├── blog.py
│   │   ├── project.py
│   │   └── rag.py            # RAG 预留
│   ├── schemas/               # 请求/响应 Schema
│   ├── services/             # 业务逻辑
│   ├── utils/                 # 工具函数
│   ├── main.py
│   └── requirements.txt
│
├── docs/                       # 开发文档
│   ├── README.md
│   └── DEVELOPMENT.md
│
└── SPEC.md                     # 项目规格文档
```

---

## 7. SEO 配置

- [x] Meta 标签（title, description, keywords）
- [x] Open Graph 标签
- [x] Twitter Card 标签
- [x] 结构化数据（JSON-LD）
- [x] Sitemap.xml 自动生成
- [x] robots.txt

---

## 8. 一期待完成清单

### 前端
- [ ] 首页 Hero 区域 + 毛玻璃导航栏
- [ ] 博客列表页 + 详情页（Markdown 渲染）
- [ ] 作品集页 + 项目详情页
- [ ] 关于页面
- [ ] RAG 入口占位页
- [ ] 明暗主题切换组件
- [ ] 响应式布局适配
- [ ] 动效骨架（入场动画、悬停效果）

### 后端
- [ ] FastAPI 项目初始化
- [ ] 博客 CRUD 接口
- [ ] 项目 CRUD 接口
- [ ] RAG 接口预留空位
- [ ] CORS 配置
- [ ] 健康检查接口

### 文档
- [ ] README.md
- [ ] DEVELOPMENT.md（开发指南）
