from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from database.base import Base


class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="进行中")
    year = Column(String(10), nullable=True)
    full_description = Column(Text, nullable=True)
    features = Column(JSON, nullable=True)
    techs = Column(JSON, nullable=True)
    demo_url = Column(String(500), nullable=True)
    repo_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
