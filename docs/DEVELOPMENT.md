# 开发指南

## 环境要求

- Node.js >= 18
- Python >= 3.10
- npm 或 yarn

## 前端开发

### 依赖安装

```bash
cd frontend
npm install
```

### 开发服务器

```bash
npm run dev
```

### 构建生产版本

```bash
npm run build
```

### 类型检查

```bash
npx vue-tsc --noEmit
```

### 添加新页面

1. 在 `src/views/` 创建新组件
2. 在 `src/router/index.ts` 添加路由

```typescript
{
  path: '/new-page',
  name: 'NewPage',
  component: () => import('@/views/NewPageView.vue')
}
```

### 添加新组件

1. 在 `src/components/` 创建组件
2. 在需要使用的页面中引入

```vue
<template>
  <div>
    <MyComponent />
  </div>
</template>

<script setup lang="ts">
import MyComponent from '@/components/MyComponent.vue'
</script>
```

### Tailwind CSS 配置

编辑 `tailwind.config.js` 自定义主题：

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        500: '#0ea5e9',
      },
    },
  },
},
```

## 后端开发

### 依赖安装

```bash
cd backend
pip install -r requirements.txt
```

### 开发服务器

```bash
uvicorn main:app --reload --port 8000
```

### API 文档

启动后访问：http://localhost:8000/docs

### 添加新接口

1. 在 `schemas/schemas.py` 定义 Pydantic 模型
2. 在 `routers/` 创建路由文件
3. 在 `main.py` 注册路由

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/items")
async def get_items():
    return [{"id": 1, "name": "Item 1"}]
```

## RAG 二期开发预留

### 需要实现的接口

| 接口 | 描述 |
|------|------|
| POST /api/rag/query | 问答查询 |
| GET /api/rag/knowledge-bases | 获取知识库列表 |
| POST /api/rag/knowledge-bases | 创建知识库 |
| DELETE /api/rag/knowledge-bases/:id | 删除知识库 |
| POST /api/rag/documents | 上传文档 |
| GET /api/rag/documents | 获取文档列表 |

### RAG 技术架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   文档上传   │ ──> │   文档解析   │ ──> │   文本分块   │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                              v
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   返回答案   │ <─  │   LLM 生成  │ <─  │  向量检索   │
└─────────────┘     └─────────────┘     └─────────────┘
                                              ^
                                              │
                                       ┌─────────────┐
                                       │  向量存储   │
                                       │  (Qdrant)   │
                                       └─────────────┘
```

### 推荐技术选型

- **Embedding**: sentence-transformers
- **向量库**: Qdrant
- **LLM**: DeepSeek-V4
- **文档解析**: LangChain + Unstructured

## SEO 配置

SEO 相关文件位于 `frontend/src/composables/useSEO.ts`

### 更新 Meta 标签

```typescript
useSEO({
  title: '页面标题',
  description: '页面描述',
  keywords: '关键词1, 关键词2'
})
```

### 结构化数据

使用 `useStructuredData` 添加 JSON-LD：

```typescript
useStructuredData('Article', {
  headline: '文章标题',
  datePublished: '2026-05-07'
})
```
