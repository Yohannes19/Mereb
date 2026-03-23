import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# On Vercel, the filesystem is read-only. If no DATABASE_URL is set, use /tmp to prevent startup crash.
if os.environ.get("VERCEL"):
    default_url = "sqlite:////tmp/mvp.db"
else:
    default_url = "sqlite:///./mvp.db"

DATABASE_URL = os.getenv("DATABASE_URL", default_url)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
