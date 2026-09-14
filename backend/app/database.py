import os
from collections.abc import Generator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool


project_root = Path(__file__).resolve().parents[2]
load_dotenv(project_root / ".env")

database_url = os.getenv("DATABASE_URL")

if database_url is None:
    raise RuntimeError("DATABASE_URL is not set.")


class Base(DeclarativeBase):
    pass


engine_options: dict[str, object] = {}
if database_url.startswith("sqlite"):
    engine_options = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }

engine = create_engine(database_url, **engine_options)

SessionLocal = sessionmaker(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
