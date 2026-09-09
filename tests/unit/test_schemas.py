"""
Tests unitarios para los schemas de Pydantic.
"""

import pytest
from datetime import date, time
from pydantic import ValidationError

from app.schemas.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    RecuperarContrasenaRequest,
    RestablecerContrasenaRequest,
)
from app.schemas.actividad import (
    ActividadBase,
    ActividadCreate,
    ActividadUpdate,
    ModalidadSchema,
    EstadoSchema,
    PersonaResponsable,
    DetallesActividad,
    MetadatosActividad,
)
from app.schemas.asistencia import (
    AsistenciaCreate,
    AsistenciaBase,
    AsistenciaRead,
)


class TestUserSchemas:
    """Tests para schemas de usuario."""

    def test_user_create_valid(self):
        """Test: Crear usuario con datos válidos."""
        user = UserCreate(
            nombre="Test User",
            username="testuser",
            email="test@example.com",
            password="securepass123",
            role="user",
        )
        assert user.nombre == "Test User"
        assert user.email == "test@example.com"

    def test_user_create_invalid_email(self):
        """Test: Email inválido lanza error."""
        with pytest.raises(ValidationError):
            UserCreate(
                nombre="Test",
                username="test",
                email="invalid_email",
                password="pass",
                role="user",
            )

    def test_user_update_optional_fields(self):
        """Test: UserUpdate permite campos opcionales."""
        user = UserUpdate(nombre="New Name")
        assert user.nombre == "New Name"
        assert user.username is None
        assert user.email is None

    def test_user_response_with_id(self):
        """Test: UserResponse incluye id."""
        user = UserResponse(
            id=1,
            nombre="Test",
            username="test",
            email="test@test.com",
            password="hashed",
            role="user",
        )
        assert user.id == 1

    def test_token_response(self):
        """Test: TokenResponse."""
        token = TokenResponse(access_token="abc123")
        assert token.access_token == "abc123"
        assert token.token_type == "bearer"

    def test_password_reset_request(self):
        """Test: Solicitud de recuperación."""
        req = RecuperarContrasenaRequest(email="test@example.com")
        assert req.email == "test@example.com"

    def test_password_reset_min_length(self):
        """Test: Contraseña debe tener mínimo 6 caracteres."""
        with pytest.raises(ValidationError):
            RestablecerContrasenaRequest(
                token="abc",
                new_password="12345",  # Muy corta
                confirm_password="12345",
            )


class TestActividadSchemas:
    """Tests para schemas de actividad."""

    def test_actividad_base_valid(self):
        """Test: ActividadBase con datos válidos."""
        act = ActividadBase(
            tema="Capacitación en Seguridad",
            actividad_id=1,
            servicio_id=1,
            subdireccion_id=1,
            modalidad_id=1,
            estado_id=1,
        )
        assert act.tema == "Capacitación en Seguridad"

    def test_actividad_base_optional_fields(self):
        """Test: Campos opcionales."""
        act = ActividadBase(
            tema="Test",
            actividad_id=1,
            servicio_id=1,
            subdireccion_id=1,
            modalidad_id=1,
            estado_id=1,
            fecha_programada=None,
            lugar_id=None,
        )
        assert act.fecha_programada is None

    def test_actividad_update_with_all_fields(self):
        """Test: ActividadUpdate con todos los campos requeridos."""
        update = ActividadUpdate(
            tema="Nuevo tema",
            actividad_id=1,
            servicio_id=1,
            subdireccion_id=1,
            modalidad_id=1,
            estado_id=1,
        )
        assert update.tema == "Nuevo tema"
        assert update.actividad_id == 1

    def test_persona_responsable_schema(self):
        """Test: Schema PersonaResponsable."""
        pr = PersonaResponsable(nombre="Juan", puesto="Ingeniero")
        assert pr.nombre == "Juan"
        assert pr.puesto == "Ingeniero"

    def test_detalles_actividad_schema(self):
        """Test: Schema DetallesActividad."""
        det = DetallesActividad(
            link="https://example.com",
            duracion="2 horas",
            grupo_dirigido="Ingenieros",
        )
        assert det.link == "https://example.com"
        assert det.duracion == "2 horas"

    def test_metadatos_actividad_schema(self):
        """Test: Schema MetadatosActividad."""
        meta = MetadatosActividad(user="admin", registro="2026-09-09")
        assert meta.user == "admin"


class TestAsistenciaSchemas:
    """Tests para schemas de asistencia."""

    def test_asistencia_create_valid(self):
        """Test: Crear asistencia con datos válidos."""
        asist = AsistenciaCreate(
            nombre_completo="Juan Pérez",
            capacitacion_id=1,
        )
        assert asist.nombre_completo == "Juan Pérez"

    def test_asistencia_create_with_optional_fields(self):
        """Test: Campos opcionales."""
        asist = AsistenciaCreate(
            nombre_completo="María García",
            sexo_id=1,
            grupo_edad_id=2,
            cui=1234567890123,
            pertenencia_cultural_id=1,
            capacitacion_id=1,
            telefono_email="maria@example.com",
        )
        assert asist.sexo_id == 1
        assert asist.cui == 1234567890123

    def test_asistencia_read_schema(self):
        """Test: AsistenciaRead con todos los campos requeridos."""
        from datetime import datetime

        asist = AsistenciaRead(
            id=1,
            nombre_completo="Test",
            capacitacion_id=1,
            fecha_registro=datetime.now(),
        )
        assert asist.id == 1


class TestModalidadSchema:
    """Tests para schema de modalidad."""

    def test_modalidad_schema(self):
        """Test: ModalidadSchema."""
        mod = ModalidadSchema(id=1, nombre="Presencial", codigo="P")
        assert mod.id == 1
        assert mod.codigo == "P"

    def test_modalidad_create(self):
        """Test: ModalidadCreate."""
        from app.schemas.actividad import ModalidadCreate

        mod = ModalidadCreate(nombre="Virtual", codigo="V")
        assert mod.nombre == "Virtual"


class TestEstadoSchema:
    """Tests para schema de estado."""

    def test_estado_schema(self):
        """Test: EstadoSchema."""
        est = EstadoSchema(id=1, nombre="Completada", codigo="C")
        assert est.codigo == "C"

    def test_estado_create(self):
        """Test: EstadoCreate."""
        from app.schemas.actividad import EstadoCreate

        est = EstadoCreate(nombre="Pendiente", codigo="P")
        assert est.nombre == "Pendiente"
