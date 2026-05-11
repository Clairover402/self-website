from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime
from database.base import Base


class AwardModel(Base):
    """
    奖项 ORM 模型

    映射到 MySQL awards 表，存储获得的奖项信息。
    使用自增整数 ID 作为主键（与 ProjectModel 一致）。
    """

    __tablename__ = "awards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    organization = Column(String(255), nullable=False)
    award_date = Column(Date, nullable=False)
    level = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)