"""Funciones de hash y HMAC para operaciones criptográficas."""

import hashlib
import hmac


def sha256_hash(value: str) -> str:
    """Calcula SHA-256 de un texto y devuelve el digest hexadecimal."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_token(token: str) -> bytes:
    """Calcula SHA-256 de un token y devuelve 32 bytes para almacenamiento binario."""
    return hashlib.sha256(token.encode("utf-8")).digest()


def hmac_hash(value: str, key: bytes) -> str:
    """Calcula un HMAC-SHA256 y devuelve el resultado hexadecimal."""
    return hmac.new(key, value.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_hmac(value: str, key: bytes, expected_hash: str) -> bool:
    """Verifica un HMAC usando comparación en tiempo constante."""
    calculated_hash = hmac_hash(value, key)
    return hmac.compare_digest(calculated_hash, expected_hash)
