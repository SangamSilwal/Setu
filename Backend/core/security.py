import bcrypt
import hashlib
import base64
from datetime import datetime, timedelta
from jose import jwt
from core.config import settings


def _prehash_password(password: str) -> bytes:
    """Pre-hash password with SHA-256 to handle any length."""
    sha256_hash = hashlib.sha256(password.encode('utf-8')).digest()
    return base64.b64encode(sha256_hash)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    prehashed = _prehash_password(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(prehashed, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    prehashed = _prehash_password(plain_password)
    return bcrypt.checkpw(prehashed, hashed_password.encode('utf-8'))


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)