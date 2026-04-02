import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:susheela2003@localhost:5432/asset_tracker"
)

# Fix for Supabase SSL connection
if "supabase" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"sslmode": "require"},
        pool_pre_ping=True,
        pool_recycle=300
    )
else:
    engine = create_engine(DATABASE_URL)

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
```

Click **"Commit changes"**!

---

## Also update DATABASE_URL in Railway to:
```
postgresql://postgres.glvsjlmobgertxkbbjwl:susheela2003@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres
