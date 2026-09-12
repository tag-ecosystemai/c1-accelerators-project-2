import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine


project_root = Path(__file__).resolve().parents[2]
load_dotenv(project_root / ".env")

database_url = os.getenv("DATABASE_URL")

if database_url is None:
    raise RuntimeError("DATABASE_URL is not set.")

engine = create_engine(database_url)