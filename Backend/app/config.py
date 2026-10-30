"""Módulo de configuración de variables de entorno."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Configuración obligatoria
    database_url: str
    secret_key: str

    # Configuración general
    app_name: str = "Internet Cafe API"
    frontend_base_url: str = "http://localhost:5173"

    # Llaves criptográficas
    jwt_private_key: str | None = None
    jwt_public_key: str | None = None
    data_enc_keys: str | None = None
    blind_index_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Instancia global de configuración
settings = Settings()