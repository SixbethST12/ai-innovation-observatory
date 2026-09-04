"""
One-time script to create the first admin user.

Run manually from the command line - not exposed via the API, since
there's no way to authenticate a request to create the first account
before any account exists. Safe to re-run: it checks for an existing
username first rather than creating duplicates.

Usage: python3 seed_admin.py
"""

import getpass

try:
    from .database import get_session, engine, Base
    from .db_models import User
except ImportError:
    from database import get_session, engine, Base
    from db_models import User

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.auth import hash_password


def create_admin():
    Base.metadata.create_all(engine)
    session = get_session()
    try:
        username = input("Admin username: ").strip()
        if not username:
            print("Username cannot be empty.")
            return

        existing = session.query(User).filter_by(username=username).first()
        if existing:
            print(f"User '{username}' already exists - not creating a duplicate.")
            return

        password = getpass.getpass("Admin password: ")
        if len(password) < 6:
            print("Password too short - use at least 6 characters.")
            return

        user = User(
            username=username,
            password_hash=hash_password(password),
            role="admin",
        )
        session.add(user)
        session.commit()
        print(f"Admin user '{username}' created successfully.")
    finally:
        session.close()


if __name__ == "__main__":
    create_admin()
