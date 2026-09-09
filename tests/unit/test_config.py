"""
Tests unitarios para la configuración del proyecto.
"""

import pytest
import os
from unittest.mock import patch


class TestDatabaseConfig:
    """Tests para la configuración de base de datos."""

    def test_secret_key_exists(self):
        """Test: SECRET_KEY está definida."""
        from app.database.config import SECRET_KEY
        assert SECRET_KEY is not None
        assert len(SECRET_KEY) > 0

    def test_algorithm_is_hs256(self):
        """Test: Algoritmo JWT es HS256."""
        from app.database.config import ALGORITHM
        assert ALGORITHM == "HS256"

    def test_token_expire_minutes(self):
        """Test: Tiempo de expiración está definido."""
        from app.database.config import ACCESS_TOKEN_EXPIRE_MINUTES
        assert ACCESS_TOKEN_EXPIRE_MINUTES > 0

    def test_mail_config_exists(self):
        """Test: Configuración de mail está definida."""
        from app.database.config import MAIL_SERVER, MAIL_PORT
        assert MAIL_SERVER is not None
        assert MAIL_PORT > 0

    @patch.dict(os.environ, {"SECRET_KEY": "test_secret_key_1234567890"})
    def test_secret_key_from_env(self):
        """Test: SECRET_KEY se carga de variables de entorno."""
        from app.database.config import _get_secret_key
        key = _get_secret_key()
        assert key == "test_secret_key_1234567890"


class TestDatabaseConnection:
    """Tests para la conexión de base de datos."""

    def test_engine_created(self):
        """Test: Engine de SQLAlchemy se crea."""
        from app.database.db import engine
        assert engine is not None

    def test_session_local_exists(self):
        """Test: SessionLocal está definido."""
        from app.database.db import SessionLocal
        assert SessionLocal is not None

    def test_base_exists(self):
        """Test: Base de SQLAlchemy está definida."""
        from app.database.db import Base
        assert Base is not None

    def test_get_db_yields_session(self):
        """Test: get_db devuelve una sesión."""
        from app.database.db import get_db

        gen = get_db()
        session = next(gen)
        assert session is not None

        try:
            next(gen)
        except StopIteration:
            pass


class TestSecurityConfig:
    """Tests para la configuración de seguridad."""

    def test_pwd_context_uses_argon2(self):
        """Test: Contexto de contraseñas usa Argon2."""
        from app.database.security import pwd_context
        assert "argon2" in pwd_context.schemes()

    def test_oauth2_scheme_exists(self):
        """Test: OAuth2 scheme está definido."""
        from app.database.security import oauth2_scheme
        assert oauth2_scheme is not None
