"""
Database connection setup.

Uses SQLite for local development (EIR-3 allows SQLite as an
alternative to PostgreSQL). SQLAlchemy is the ORM - it lets us define
tables as Python classes (in db_models.py) instead of writing raw SQL.

The database file will be created automatically on first run at
backend/app/db/observatory.db - this file should NOT be committed to
git (it's already covered by *.db in .gitignore).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "observatory.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


def get_session():
    """Returns a new database session. Caller is responsible for closing it."""
    return SessionLocal()


if __name__ == "__main__":
    # Self-test: confirm the engine connects and the file gets created
    print(f"Database URL: {DATABASE_URL}")
    with engine.connect() as conn:
        print("Connection successful")
    print(f"Database file exists: {os.path.exists(DB_PATH)}")
