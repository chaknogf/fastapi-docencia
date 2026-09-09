"""
Tests unitarios para el módulo de seguridad.
"""

import pytest
from datetime import timedelta
from jose import jwt

from app.database.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    pwd_context,
)
from app.database.config import SECRET_KEY, ALGORITHM


class TestPasswordHashing:
    """Tests para hashing de contraseñas."""

    def test_hash_password(self):
        """Test: Generar hash de contraseña."""
        password = "mi_contrasena_segura"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Test: Verificar contraseña correcta."""
        password = "mi_contrasena"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test: Verificar contraseña incorrecta."""
        password = "mi_contrasena"
        hashed = hash_password(password)

        assert verify_password("contraseña_incorrecta", hashed) is False

    def test_different_hashes_same_password(self):
        """Test: Mismo password genera hashes diferentes (salt único)."""
        password = "misma_contraseña"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2
        # Pero ambos son válidos
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Tests para tokens JWT."""

    def test_create_access_token(self):
        """Test: Crear token de acceso."""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        assert token is not None
        assert len(token) > 0

    def test_create_token_with_custom_expiry(self):
        """Test: Crear token con expiración personalizada."""
        data = {"sub": "testuser"}
        expires = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires)

        assert token is not None

    def test_create_token_with_purpose(self):
        """Test: Crear token con propósito específico."""
        data = {"sub": "testuser"}
        token = create_access_token(data, purpose="password_reset")

        payload = decode_access_token(token)
        assert payload.get("purpose") == "password_reset"

    def test_decode_valid_token(self):
        """Test: Decodificar token válido."""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        payload = decode_access_token(token)

        assert payload.get("sub") == "testuser"
        assert "exp" in payload

    def test_decode_invalid_token(self):
        """Test: Error al decodificar token inválido."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("token_invalido")

        assert exc_info.value.status_code == 401

    def test_token_contains_correct_algorithm(self):
        """Test: Token usa el algoritmo correcto."""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        # Decodificar sin verificar para ver el header
        import base64
        import json

        parts = token.split(".")
        header = json.loads(base64.urlsafe_b64decode(parts[0] + "=="))

        assert header.get("alg") == ALGORITHM


class TestPasswordContext:
    """Tests para el contexto de contraseñas."""

    def test_uses_argon2(self):
        """Test: Usa Argon2 como algoritmo."""
        assert "argon2" in pwd_context.schemes()

    def test_hash_is_argon2_format(self):
        """Test: El hash tiene formato Argon2."""
        hashed = pwd_context.hash("test")
        assert hashed.startswith("$argon2")
