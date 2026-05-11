from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from database.base import Base


class BlogModel(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    excerpt = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    cover = Column(String(500), nullable=True)
    tags = Column(JSON, nullable=True)
    read_time = Column(Integer, default=0)
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
