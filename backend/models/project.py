from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from database.base import Base


class ProjectModel(Base):
    """
    项目 ORM 模型

    映射到 MySQL projects 表，存储作品集项目的完整信息。
    与 BlogModel 不同，项目使用自增整数 ID 而非 slug 作为主键标识。
    """

    __tablename__ = "projects"

    # 主键：自增整数 ID
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 基本信息
    name = Column(String(255), nullable=False)          # 项目名称
    description = Column(Text, nullable=False)           # 简短描述（列表页展示）
    icon = Column(String(100), nullable=True)            # 图标（emoji 或图标名）
    status = Column(String(50), nullable=False, default="进行中")  # 项目状态
    year = Column(String(10), nullable=True)             # 项目年份

    # 详细内容
    full_description = Column(Text, nullable=True)       # 完整描述（详情页展示）
    features = Column(JSON, nullable=True)               # 功能特性列表（JSON 数组）
    techs = Column(JSON, nullable=True)                  # 技术栈列表（JSON 数组）

    # 外部链接
    demo_url = Column(String(500), nullable=True)        # 演示地址
    repo_url = Column(String(500), nullable=True)        # 仓库地址

    # 时间戳
    created_at = Column(DateTime, default=datetime.now)                        # 创建时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now) # 更新时间（与 BlogModel 对齐）
