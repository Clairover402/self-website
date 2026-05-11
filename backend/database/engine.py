from sqlalchemy import create_engine
from core.config import settings
from database.base import Base

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args=connect_args
)


def init_db():
    Base.metadata.create_all(bind=engine)
