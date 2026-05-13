"""
Seed script - populates the database with sample data.

Run: cd backend && python seed.py

Idempotent: skips insertion if data already exists.
"""
import sys
sys.path.insert(0, ".")

from database.engine import init_db, engine
from database.session import SessionLocal
from models.blog import BlogModel
from models.project import ProjectModel
from models.award import AwardModel
from sqlalchemy import select
from datetime import date


def seed():
    init_db()
    db = SessionLocal()

    # --- Blogs ---
    existing = db.execute(select(BlogModel).where(BlogModel.slug == "vue3-composition-api")).scalars().first()
    if not existing:
        blogs = [
            BlogModel(
                title="Vue 3 Composition API 完全指南",
                slug="vue3-composition-api",
                excerpt="深入探索 Vue 3 的 Composition API，学习如何构建更灵活、更可维护的组件。",
                content="""# Vue 3 Composition API 完全指南

## 引言

Vue 3 引入了全新的 Composition API，这是一种组织组件逻辑的新方式。与传统的 Options API 相比，Composition API 提供了更灵活、更强大的代码组织能力。

## 为什么使用 Composition API？

### 1. 更好的逻辑复用

使用 Composition API，我们可以轻松地将相关逻辑提取到可复用的函数中，称为"组合式函数"（Composables）。

### 2. 更灵活的代码组织

在大型组件中，相关逻辑可能分散在不同的选项中。Composition API 允许我们将相关逻辑放在一起。

### 3. 更好的类型推断

配合 TypeScript，Composition API 提供了更好的类型推断支持。

## 核心概念

### ref 和 reactive

```javascript
import { ref, reactive } from "vue"

const count = ref(0)
const state = reactive({ name: "Vue 3" })
```

### computed

```javascript
const doubled = computed(() => count.value * 2)
```

## 总结

Composition API 是 Vue 3 最重要的特性之一，掌握它将帮助您构建更好的应用。
""",
                cover="📗",
                tags=["Vue", "前端"],
                read_time=8,
            ),
            BlogModel(
                title="FastAPI 最佳实践",
                slug="fastapi-best-practices",
                excerpt="掌握 FastAPI 的核心概念，学习如何构建高性能的 Python RESTful API。",
                content="""# FastAPI 最佳实践

## 引言

FastAPI 是一个现代、高性能的 Python Web 框架，专为构建 API 而设计。

## 核心特性

### 自动文档生成

FastAPI 自动生成 Swagger UI 和 ReDoc 文档。

### 类型安全

基于 Pydantic 的请求/响应验证。

### 异步支持

原生支持 async/await，轻松处理并发请求。

## 项目结构建议

```
backend/
├── routers/
├── services/
├── models/
├── schemas/
└── core/
```

## 总结

FastAPI 是构建现代 API 的最佳选择之一。
""",
                cover="🚀",
                tags=["Python", "后端"],
                read_time=12,
            ),
            BlogModel(
                title="Docker 容器化部署完全指南",
                slug="docker-deployment",
                excerpt="从零开始学习 Docker，掌握容器化技术的精髓。",
                content="""# Docker 容器化部署完全指南

## 引言

Docker 改变了我们构建、部署和运行应用的方式。

## 核心概念

### 镜像（Image）
镜像是一个只读模板，包含运行应用所需的一切。

### 容器（Container）
容器是镜像的运行实例。

### Dockerfile

```dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

## 总结

掌握 Docker 是每个开发者的必备技能。
""",
                cover="🐳",
                tags=["DevOps", "Docker"],
                read_time=10,
            ),
        ]
        db.add_all(blogs)
        print(f"Inserted {len(blogs)} blogs")

    # --- Projects ---
    existing = db.execute(select(ProjectModel).where(ProjectModel.name == "RAG 智能知识库系统")).scalars().first()
    if not existing:
        projects = [
            ProjectModel(
                name="RAG 智能知识库系统",
                description="基于向量数据库和 LLM 的智能问答系统，支持多文档解析与多轮对话。",
                icon="🧻",
                status="进行中",
                year="2026",
                full_description="这是一个完整的企业级 RAG 知识库系统，支持多格式文档上传、智能分块、向量存储和语义检索。结合 LLM 提供精准的问答服务。",
                features=["多格式文档解析", "语义向量检索", "多知识库管理", "多轮对话", "权限管理"],
                techs=["Python", "FastAPI", "Qdrant", "Vue 3", "LangChain"],
                demo_url="https://demo.example.com",
                repo_url="https://github.com/example/rag-system",
            ),
            ProjectModel(
                name="实时协作白板",
                description="支持多人实时协作的在线白板工具，集成绘图、流程图和思维导图功能。",
                icon="🎹",
                status="已完成",
                year="2025",
                full_description="基于 WebSocket 的实时协作白板，支持绘图、流程图、思维导图等多种工具。",
                features=["实时协作", "多种绘图工具", "导出 PNG/SVG", "历史版本"],
                techs=["React", "WebSocket", "Canvas", "Node.js", "Redis"],
                demo_url="https://whiteboard.example.com",
                repo_url="https://github.com/example/whiteboard",
            ),
            ProjectModel(
                name="电商微服务平台",
                description="基于微服务架构的电商平台，包含用户、商品、订单、支付等核心模块。",
                icon="📦",
                status="已完成",
                year="2025",
                full_description="完整的微服务电商平台，使用 Go + gRPC 构建。",
                features=["微服务架构", "gRPC 通信", "Docker 部署", "K8s 编排"],
                techs=["Go", "gRPC", "Docker", "Kubernetes", "PostgreSQL"],
                repo_url="https://github.com/example/ecommerce",
            ),
        ]
        db.add_all(projects)
        print(f"Inserted {len(projects)} projects")

    # --- Awards ---
    existing = db.execute(select(AwardModel).where(AwardModel.title == "全国大学生程序设计竞赛")).scalars().first()
    if not existing:
        awards = [
            AwardModel(
                title="全国大学生程序设计竞赛",
                organization="教育部",
                award_date=date(2024, 6, 15),
                level="国家级",
            ),
            AwardModel(
                title="省级优秀毕业生",
                organization="省教育厅",
                award_date=date(2025, 7, 1),
                level="省级",
            ),
            AwardModel(
                title="校创新创业大赛",
                organization="校团委",
                award_date=date(2024, 11, 20),
                level="一等奖",
            ),
        ]
        db.add_all(awards)
        print(f"Inserted {len(awards)} awards")

    db.commit()
    db.close()
    print("Seed completed!")


if __name__ == "__main__":
    seed()
