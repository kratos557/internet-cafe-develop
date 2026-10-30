import hashlib
import pytest
import jwt

from cryptography.hazmat.primitives.asymmetric import ec
from app.security import crypto_utils, jwt_utils


def test_sha256_hash():
    assert crypto_utils.sha256_hash("usuario123") == hashlib.sha256(b"usuario123").hexdigest()


def test_hash_token():
    result = crypto_utils.hash_token("token-prueba")
    assert isinstance(result, bytes)
    assert len(result) == 32


def test_hmac_hash_and_verify():
    key = b"K" * 32
    value = "usuario123"
    generated = crypto_utils.hmac_hash(value, key)

    assert crypto_utils.verify_hmac(value, key, generated)
    assert not crypto_utils.verify_hmac("otro-usuario", key, generated)


def test_jwt_create_and_verify(monkeypatch):
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    monkeypatch.setattr(jwt_utils, "get_jwt_private_key", lambda: private_key)
    monkeypatch.setattr(jwt_utils, "get_jwt_public_key", lambda: public_key)

    token = jwt_utils.create_access_token("usuario-prueba")
    payload = jwt_utils.verify_access_token(token)

    assert payload["sub"] == "usuario-prueba"
    assert "iat" in payload
    assert "exp" in payload


def test_jwt_rejects_invalid_token(monkeypatch):
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    monkeypatch.setattr(jwt_utils, "get_jwt_public_key", lambda: public_key)

    with pytest.raises(jwt.InvalidTokenError):
        jwt_utils.verify_access_token("token-invalido")


def test_jwt_rejects_empty_user():
    with pytest.raises(ValueError):
        jwt_utils.create_access_token("")

import base64
import json

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from app.security import keys


def test_load_data_enc_keys(monkeypatch):
    original_key = b"A" * 32
    encoded = base64.b64encode(original_key).decode("ascii")

    monkeypatch.setattr(
        keys.settings,
        "data_enc_keys",
        json.dumps({"key1": encoded}),
    )

    assert keys.get_data_enc_keys() == {"key1": original_key}


def test_reject_invalid_data_enc_key_length(monkeypatch):
    encoded = base64.b64encode(b"A" * 16).decode("ascii")

    monkeypatch.setattr(
        keys.settings,
        "data_enc_keys",
        json.dumps({"key1": encoded}),
    )

    with pytest.raises(RuntimeError):
        keys.get_data_enc_keys()


def test_load_blind_index_key(monkeypatch):
    original_key = b"B" * 32
    encoded = base64.b64encode(original_key).decode("ascii")

    monkeypatch.setattr(keys.settings, "blind_index_key", encoded)

    assert keys.get_blind_index_key() == original_key


def test_reject_short_blind_index_key(monkeypatch):
    encoded = base64.b64encode(b"B" * 16).decode("ascii")

    monkeypatch.setattr(keys.settings, "blind_index_key", encoded)

    with pytest.raises(RuntimeError):
        keys.get_blind_index_key()


def test_load_jwt_pem_keys(monkeypatch):
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode("utf-8")

    public_pem = public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    monkeypatch.setattr(keys.settings, "jwt_private_key", private_pem)
    monkeypatch.setattr(keys.settings, "jwt_public_key", public_pem)

    assert isinstance(keys.get_jwt_private_key(), ec.EllipticCurvePrivateKey)
    assert isinstance(keys.get_jwt_public_key(), ec.EllipticCurvePublicKey)


def test_reject_wrong_jwt_curve(monkeypatch):
    private_key = ec.generate_private_key(ec.SECP384R1())

    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode("utf-8")

    monkeypatch.setattr(keys.settings, "jwt_private_key", private_pem)

    with pytest.raises(RuntimeError):
        keys.get_jwt_private_key()
