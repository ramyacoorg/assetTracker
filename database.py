
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()  # Load .env file

_db_url_from_env = os.getenv("DATABASE_URL")
if not _db_url_from_env:
    raise RuntimeError("DATABASE_URL environment variable is not set!")
DATABASE_URL = _db_url_from_env

# Always force SSL since we only use cloud Postgres (Supabase)
_connect_args = {"sslmode": "require", "options": "-c client_encoding=utf8"}

engine = create_engine(
    DATABASE_URL,
    connect_args=_connect_args,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_timeout=30
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
