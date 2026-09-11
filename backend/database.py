import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite Database Configuration
# Saves rakshak.db inside the backend directory by default
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'rakshak.db')}")

# Create engine with check_same_thread=False for SQLite multithread compatibility
engine = create_engine(
    DB_PATH,
    connect_args={"check_same_thread": False} if DB_PATH.startswith("sqlite") else {},
    echo=False
)

# SessionLocal class for instantiating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for SQLAlchemy models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a new SQLAlchemy session per request
    and ensures clean closure after completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Ensures all database tables defined in models.py are created in SQLite.
    """
    import models  # noqa: F401 - Imported to register models with Base.metadata
    Base.metadata.create_all(bind=engine)
