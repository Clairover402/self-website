"""
枚举常量模块

定义项目中使用的所有枚举类型。
将松散字符串约束为强类型枚举，提供：
- API 文档自动展示可选值（Swagger UI 下拉选择）
- 编译期校验，拼写错误在请求进入时就暴露
- 统一管理标签列表，修改只需改一处
"""

from enum import Enum


class BlogTag(str, Enum):
    """
    博客标签枚举

    继承 str 使其可直接用于 JSON 序列化，同时保留枚举的校验能力。
    共 10 个标签，覆盖主流技术领域，博客发布时必须从这些标签中选择。

    使用示例：
        tags=[BlogTag.PYTHON, BlogTag.AI]
        BlogTag("python")  # => BlogTag.PYTHON
    """

    # 前端生态
    FRONTEND = "前端"          # HTML/CSS/JS/TS/浏览器 API
    VUE = "Vue"                # Vue 3 / Nuxt / Pinia 等 Vue 生态
    JAVASCRIPT = "JavaScript"  # JS/TS 语言特性及运行时

    # 后端生态
    BACKEND = "后端"           # 服务端架构 / API 设计 / 中间件
    PYTHON = "Python"          # Python 语言及生态（FastAPI/Django 等）

    # AI / 数据
    AI = "AI"                  # 机器学习 / 深度学习 / LLM / RAG

    # 基础设施
    DEVOPS = "DevOps"          # CI/CD / Docker / K8s / 云原生
    DATABASE = "数据库"        # SQL/NoSQL / 建模 / 优化

    # 通用
    SECURITY = "安全"          # Web 安全 / 认证授权 / 加密
    ARCHITECTURE = "架构"      # 系统设计 / 设计模式 / 领域驱动

    @classmethod
    def all_values(cls) -> list[str]:
        """返回所有枚举值（字符串列表），供 CRUD 层动态引用"""
        return [member.value for member in cls]

    @classmethod
    def all_labels(cls) -> list[str]:
        """返回所有枚举成员的名称，供文档生成"""
        return [member.name for member in cls]


class AwardLevel(str, Enum):
    """
    奖项级别枚举

    继承 str 使其可直接用于 JSON 序列化，同时保留枚举的校验能力。
    共 9 个级别，覆盖常见奖项分类。
    """

    NATIONAL = "国家级"
    PROVINCIAL = "省级"
    MUNICIPAL = "市级"
    SCHOOL = "校级"
    FIRST_PRIZE = "一等奖"
    SECOND_PRIZE = "二等奖"
    THIRD_PRIZE = "三等奖"
    EXCELLENCE = "优秀奖"
    OTHER = "其他"

    @classmethod
    def all_values(cls) -> list[str]:
        """返回所有枚举值（字符串列表）"""
        return [member.value for member in cls]

    @classmethod
    def all_labels(cls) -> list[str]:
        """返回所有枚举成员的名称"""
        return [member.name for member in cls]