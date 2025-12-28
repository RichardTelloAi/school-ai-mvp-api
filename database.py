# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# -------------------------------------------------------------------
# Database configuration
# -------------------------------------------------------------------

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# SQLAlchemy engine (2.x compatible)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

# -------------------------------------------------------------------
# Session factory
# -------------------------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)

# -------------------------------------------------------------------
# FastAPI dependency
# -------------------------------------------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

