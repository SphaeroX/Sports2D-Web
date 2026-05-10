import uuid
import secrets
import hashlib

def generate_job_id() -> str:
    """Generate a secure unique job identifier."""
    return secrets.token_urlsafe(24)

def generate_access_token() -> str:
    """Generate an additional access token for result downloads."""
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    """Hash a token for storage."""
    return hashlib.sha256(token.encode()).hexdigest()
