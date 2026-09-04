"""
Authentication - NFR-2 (admin functions require authentication).

Handles password hashing (bcrypt) and JWT token creation/verification.

FIX: originally used passlib as a wrapper around bcrypt, but passlib
1.7.4 has a known compatibility break with bcrypt 4.0+ (removed an
internal attribute passlib's version-detection relied on, causing a
confusing "password too long" error unrelated to the actual input).
Fixed by calling bcrypt directly - simpler, avoids the buggy
compatibility layer entirely.
"""

import os
import bcrypt
import jwt
from datetime import datetime, timedelta, UTC
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


def hash_password(plain_password: str) -> str:
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))


def create_token(username: str, role: str) -> str:
    expire = datetime.now(UTC) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {"sub": username, "role": role, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


if __name__ == "__main__":
    if not SECRET_KEY or SECRET_KEY == "YOUR_GENERATED_KEY":
        print("ERROR: JWT_SECRET_KEY is missing or still the placeholder - fix .env first")
    else:
        test_password = "test123"
        hashed = hash_password(test_password)
        print("Hashed:", hashed[:30], "...")
        print("Verify correct password:", verify_password(test_password, hashed))
        print("Verify wrong password:", verify_password("wrongpass", hashed))

        token = create_token("testadmin", "admin")
        print("\nToken:", token[:40], "...")
        decoded = decode_token(token)
        print("Decoded payload:", decoded)
