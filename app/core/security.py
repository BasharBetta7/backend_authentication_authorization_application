import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from datetime import datetime, timedelta
from uuid import uuid4

from jose import jwt 



_ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", "60"))
_AUTH_SECRET = os.getenv("AUTH_SECRET", "change-me-in-production")
_PBKDF2_ITERATIONS = int(os.getenv("PASSWORD_HASH_ITERATIONS", "120000"))


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(f"{data}{padding}".encode("utf-8"))


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${_PBKDF2_ITERATIONS}${_b64url_encode(salt)}${_b64url_encode(derived_key)}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_str, salt_b64, expected_b64 = password_hash.split("$", maxsplit=3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_str)
        salt = _b64url_decode(salt_b64)
        expected = _b64url_decode(expected_b64)
    except (ValueError, TypeError):
        return False

    derived_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(derived_key, expected)


def create_access_token(data: dict) -> str:
    """Create JWT access token - easiest way!"""
    expire = datetime.utcnow() + timedelta(seconds=_ACCESS_TOKEN_EXPIRE_SECONDS)
    data_copy = data.copy()
    data_copy.update({"exp": expire})
    return jwt.encode(data_copy, _AUTH_SECRET, algorithm="HS256")

def create_refresh_token(subject: str | int) -> tuple[str, str, datetime]:
    now = datetime.now()
    expire = datetime.now() + timedelta(days=1)
    jti = str(uuid4())

    payload = {
        "sub": str(subject),
        "jti": jti,
        "type": "refresh",
        "iat" : now, 
        "exp" : expire
    }
    token = jwt.encode(payload, _AUTH_SECRET , algorithm="HS256")
    return token, jti, expire




def verify_access_token(token: str) -> dict | None:
    """Verify and decode JWT access token - easiest way!"""
    try:
        return jwt.decode(token, _AUTH_SECRET, algorithms=["HS256"])
    except jwt.JWTError:
        return None


