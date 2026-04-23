
import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()  # Load .env file

# Build DATABASE_URL safely to handle special characters (like @) in the password.
# Railway's Variables UI may store the raw password value, causing double-@ parse errors.
# We use individual component env vars so urllib.parse.quote handles encoding correctly.
_db_host     = os.getenv("DB_HOST",     "db.glvsjlmobgertxkbbjwl.supabase.co")
_db_port     = os.getenv("DB_PORT",     "5432")
_db_name     = os.getenv("DB_NAME",     "postgres")
_db_user     = os.getenv("DB_USER",     "postgres")
_db_password = os.getenv("DB_PASSWORD", "susheela@2003")

_encoded_pw  = urllib.parse.quote(_db_password, safe="")
DATABASE_URL = os.getenv("DATABASE_URL") or \
    f"postgresql://{_db_user}:{_encoded_pw}@{_db_host}:{_db_port}/{_db_name}"

# Always use SSL for Supabase cloud Postgres
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
