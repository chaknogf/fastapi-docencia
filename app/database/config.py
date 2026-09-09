"""
Configuración global de la aplicación.
NO poner aquí lógica, solo constantes y variables de entorno.
"""

from datetime import timedelta
import os
import secrets
from dotenv import load_dotenv

# Cargar .env (si existe)
load_dotenv(override=True)


def _get_required_env(key: str) -> str:
    """Obtiene una variable de entorno requerida. Lanza error si no existe."""
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Variable de entorno requerida no encontrada: {key}. "
            f"Definirla en .env o en el entorno del sistema."
        )
    return value


def _get_secret_key() -> str:
    """
    Obtiene SECRET_KEY de variables de entorno.
    En producción DEBE estar definida. En desarrollo genera una temporal.
    """
    env_key = os.getenv("SECRET_KEY")
    if env_key:
        return env_key

    # Solo para desarrollo - en producción fallará
    is_production = os.getenv("ENVIRONMENT", "development") == "production"
    if is_production:
        raise EnvironmentError(
            "SECRET_KEY es obligatoria en producción. "
            "Genera una con: python -c \"import secrets; print(secrets.token_hex(32))\""
        )

    print("⚠️  ADVERTENCIA: Usando SECRET_KEY temporal. Configurar en producción.")
    return secrets.token_hex(32)


# ======================
# JWT CONFIG
# ======================
SECRET_KEY = _get_secret_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24h

# ======================
# DATABASE CONFIG
# ======================
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "docencia")

# ======================
# MAIL CONFIG
# ======================
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM", "ticshosptecpan@gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_TLS = os.getenv("MAIL_TLS", "true").lower() == "true"
MAIL_SSL = os.getenv("MAIL_SSL", "false").lower() == "true"

# ======================
# ENVIRONMENT
# ======================
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"
