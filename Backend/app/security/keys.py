"""Carga segura de llaves criptográficas desde el entorno o archivos locales."""

import base64
import json
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from app.config import settings


BACKEND_DIR = Path(__file__).resolve().parents[2]
KEYS_DIR = BACKEND_DIR / ".local" / "keys"


def _read_pem(env_name: str, default_file: str) -> bytes:
    """Lee una llave PEM desde configuración o desde un archivo local."""
    value = getattr(settings, env_name.lower(), None)

    if value:
        return value.replace("\\n", "\n").encode("utf-8")

    path = KEYS_DIR / default_file

    if not path.is_file():
        raise RuntimeError(
            f"No se encontró la llave {default_file}. "
            f"Configura {env_name} o créala en {path}."
        )

    return path.read_bytes()


def get_jwt_private_key():
    """Carga una llave privada EC P-256 compatible con ES256."""
    try:
        key = serialization.load_pem_private_key(
            _read_pem("JWT_PRIVATE_KEY", "jwt_es256_private.pem"),
            password=None,
        )
    except (ValueError, TypeError) as error:
        raise RuntimeError(
            "JWT_PRIVATE_KEY no contiene una llave PEM válida"
        ) from error

    if not isinstance(key, ec.EllipticCurvePrivateKey) or not isinstance(
        key.curve, ec.SECP256R1
    ):
        raise RuntimeError(
            "JWT_PRIVATE_KEY debe ser una llave EC de curva P-256"
        )

    return key


def get_jwt_public_key():
    """Carga una llave pública EC P-256 compatible con ES256."""
    try:
        key = serialization.load_pem_public_key(
            _read_pem("JWT_PUBLIC_KEY", "jwt_es256_public.pem")
        )
    except (ValueError, TypeError) as error:
        raise RuntimeError(
            "JWT_PUBLIC_KEY no contiene una llave PEM válida"
        ) from error

    if not isinstance(key, ec.EllipticCurvePublicKey) or not isinstance(
        key.curve, ec.SECP256R1
    ):
        raise RuntimeError(
            "JWT_PUBLIC_KEY debe ser una llave EC de curva P-256"
        )

    return key


def get_data_enc_keys() -> dict[str, bytes]:
    """Carga un anillo JSON de llaves AES-256 codificadas en Base64."""
    raw = settings.data_enc_keys

    if not raw:
        raise RuntimeError("Falta configurar DATA_ENC_KEYS")

    try:
        encoded_keys = json.loads(raw)

        if not isinstance(encoded_keys, dict) or not encoded_keys:
            raise ValueError("Se esperaba un objeto JSON no vacío")

        decoded = {}

        for key_id, value in encoded_keys.items():
            if not isinstance(key_id, str) or not key_id:
                raise ValueError("El identificador de llave no puede estar vacío")

            if not isinstance(value, str):
                raise ValueError("Cada llave debe ser una cadena Base64")

            key_bytes = base64.b64decode(value, validate=True)

            if len(key_bytes) != 32:
                raise ValueError(
                    f"La llave {key_id} debe contener exactamente 32 bytes"
                )

            decoded[key_id] = key_bytes

        return decoded

    except (ValueError, TypeError) as error:
        raise RuntimeError(
            "DATA_ENC_KEYS debe ser un objeto JSON con llaves AES-256 en Base64"
        ) from error


def get_blind_index_key() -> bytes:
    """Carga la llave HMAC para índices ciegos, codificada en Base64."""
    raw = settings.blind_index_key

    if not raw:
        raise RuntimeError("Falta configurar BLIND_INDEX_KEY")

    try:
        key = base64.b64decode(raw, validate=True)
    except (ValueError, TypeError) as error:
        raise RuntimeError(
            "BLIND_INDEX_KEY debe estar codificada en Base64"
        ) from error

    if len(key) < 32:
        raise RuntimeError(
            "BLIND_INDEX_KEY debe contener al menos 32 bytes"
        )

    return key