"""
Tests de integración para los endpoints de usuarios.
"""

import pytest
from fastapi.testclient import TestClient


class TestUserEndpoints:
    """Tests para endpoints de usuarios."""

    def test_get_users_requires_auth(self, client):
        """Test: Listar usuarios requiere autenticación."""
        response = client.get("/fad/user/")
        assert response.status_code in [401, 403]

    def test_health_endpoint(self, client):
        """Test: Health check funciona."""
        response = client.get("/fad/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_create_user_requires_auth(self, client):
        """Test: Crear usuario requiere autenticación."""
        user_data = {
            "nombre": "Test",
            "username": "test",
            "email": "test@test.com",
            "password": "pass123",
            "role": "user",
        }
        response = client.post("/fad/user/crear", json=user_data)
        assert response.status_code in [401, 403]


class TestActividadEndpoints:
    """Tests para endpoints de actividades."""

    def test_listar_actividades(self, client):
        """Test: Listar actividades no requiere auth (público)."""
        response = client.get("/fad/actividades/")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "actividades" in data

    def test_crear_actividad_requires_auth(self, client):
        """Test: Crear actividad requiere autenticación."""
        actividad_data = {
            "tema": "Test",
            "actividad_id": 1,
            "servicio_id": 1,
            "subdireccion_id": 1,
            "modalidad_id": 1,
            "estado_id": 1,
        }
        response = client.post("/fad/actividad/crear/", json=actividad_data)
        assert response.status_code in [401, 403]

    def test_reporte_vista(self, client):
        """Test: Reporte vista funciona."""
        response = client.get("/fad/reporte/vista")
        # Puede retornar 200 o 404 si no hay datos
        assert response.status_code in [200, 404]

    def test_reporte_resumen_anual(self, client):
        """Test: Reporte resumen anual funciona."""
        response = client.get("/fad/reporte/resumen-anual")
        assert response.status_code in [200, 404]


class TestAsistenciaEndpoints:
    """Tests para endpoints de asistencia."""

    def test_listar_asistencias_requires_auth(self, client):
        """Test: Listar asistencias requiere autenticación."""
        response = client.get("/fad/asistencia/")
        assert response.status_code in [401, 403]

    def test_crear_asistencia_requires_auth(self, client):
        """Test: Crear asistencia requiere autenticación."""
        asistencia_data = {
            "nombre_completo": "Test User",
            "capacitacion_id": 1,
        }
        response = client.post("/fad/asistencia/", json=asistencia_data)
        assert response.status_code in [401, 403]


class TestAuthEndpoints:
    """Tests para endpoints de autenticación."""

    def test_auth_email_without_data(self, client):
        """Test: Auth email sin datos retorna error."""
        response = client.post("/fad/auth/email", json={})
        assert response.status_code == 400

    def test_auth_email_invalid_format(self, client):
        """Test: Auth email con formato inválido."""
        response = client.post("/fad/auth/email", json={"email": "invalid"})
        assert response.status_code == 400


class TestVerificadorEndpoint:
    """Tests para el verificador de horarios."""

    def test_verificador_invalid_date(self, client):
        """Test: Verificador con fecha inválida."""
        response = client.post("/fad/verificador/?fecha=invalid")
        assert response.status_code == 400

    def test_verificador_valid_date(self, client):
        """Test: Verificador con fecha válida."""
        response = client.post("/fad/verificador/?fecha=2026-09-15")
        assert response.status_code == 200
        data = response.json()
        assert "valido" in data
        assert "coincidencias" in data


class TestDocEndpoints:
    """Tests para documentación."""

    def test_docs_accessible(self, client):
        """Test: Documentación Swagger accesible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema(self, client):
        """Test: Schema OpenAPI accesible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
