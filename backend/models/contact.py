"""Contact ORM model - stores visitor messages."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from database.base import Base


class ContactModel(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
