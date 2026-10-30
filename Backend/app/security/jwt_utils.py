"""Emisión y verificación de tokens JWT mediante ES256."""

from datetime import datetime, timedelta, timezone

import jwt

from app.security.keys import get_jwt_private_key, get_jwt_public_key

ALGORITHM = "ES256"
TOKEN_DURATION_MINUTES = 10


def create_access_token(user_id: str) -> str:
    """Genera un JWT ES256 para un usuario."""
    if user_id is None or not str(user_id).strip():
        raise ValueError("user_id no puede estar vacío")

    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=TOKEN_DURATION_MINUTES),
    }
    return jwt.encode(payload, get_jwt_private_key(), algorithm=ALGORITHM)


def verify_access_token(token: str) -> dict:
    """Verifica firma, algoritmo y expiración de un JWT ES256."""
    if not isinstance(token, str) or not token:
        raise ValueError("El token JWT no puede estar vacío")

    return jwt.decode(
        token,
        get_jwt_public_key(),
        algorithms=[ALGORITHM],
        options={"require": ["sub", "iat", "exp"]},
    )
