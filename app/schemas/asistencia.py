from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class AsistenciaBase(BaseModel):
    nombre_completo: str = Field(..., max_length=150)
    sexo_id: Optional[int] = Field(None, description="ID de la tabla sexo")
    grupo_edad_id: Optional[int] = Field(None, description="ID del grupo de edad")
    cui: Optional[int] = Field(None, description="CUI del participante")
    puesto_funcional: Optional[str] = Field(None, max_length=100)
    pertenencia_cultural_id: Optional[int] = Field(None, description="ID de pertenencia cultural")
    telefono_email: Optional[str] = Field(None, max_length=150)
    datos_extras: Optional[Any] = Field(None, description="Campo JSON con información adicional")
    capacitacion_id: int = Field(..., description="ID de la actividad o capacitación relacionada")


class AsistenciaCreate(AsistenciaBase):
    """Schema para crear registros de asistencia"""
    pass


class AsistenciaRead(AsistenciaBase):
    """Schema para leer registros de asistencia"""
    id: int
    fecha_registro: datetime

    class Config:
        from_attributes = True  # Permite compatibilidad con modelos SQLAlchemy