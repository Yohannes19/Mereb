import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")
print("DB URL:", TURSO_DATABASE_URL)
print("TOKEN:", TURSO_AUTH_TOKEN)

if TURSO_DATABASE_URL and TURSO_AUTH_TOKEN:
    DATABASE_URL = f"{TURSO_DATABASE_URL}?authToken={TURSO_AUTH_TOKEN}"
else:
    DATABASE_URL = "sqlite:///./mvp.db"

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
