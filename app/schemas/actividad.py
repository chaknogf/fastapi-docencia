from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field as field


# Subesquema para persona responsable
class PersonaResponsable(BaseModel):
    nombre: Optional[str] = field(default=None)
    puesto: Optional[str] = field(default=None)

# Subesquema para detalles de la actividad
class DetallesActividad(BaseModel):
    link: Optional[str] = field(default=None)
    duracion: Optional[str] = field(default=None)
    grupo_dirigido: Optional[str] = field(default=None)
    lugar: Optional[str] = field(default=None)
    contenido: Optional[str] = field(default=None)
    asistencia: Optional[int] = field(default=None)
    inasistencia: Optional[int] = field(default=None)
    excelente: Optional[int] = field(default=None)
    bueno: Optional[int] = field(default=None)
    regular: Optional[int] = field(default=None)
    deficiente: Optional[int] = field(default=None)
    fecha_entrega_informe: Optional[str] = field(default=None)
    mes: Optional[int] = field(default=None)

# Subesquema para metadatos
class MetadatosActividad(BaseModel):
    user: Optional[str] = field(default=None)
    registro: Optional[str] = field(default=None)


class ActividadBase(BaseModel):
    id: int
    tema: str = field(...)
    actividad: int = field(...)
    servicio_encargado: str = field(...)
    persona_responsable: Optional[Dict[str, PersonaResponsable]] = field(default=None)
    tiempo_aproximado: Optional[str] = field(default=None)
    fechas_a_desarrollar: Optional[str] = field(default=None)
    modalidad: str = field(..., min_length=1, max_length=2)
    estado: str = field(..., min_length=1, max_length=2)
    detalles: Optional[DetallesActividad] = field(default=None)
    metadatos: Optional[MetadatosActividad] = field(default=None)

class ActividadCreate(ActividadBase):
    """Esquema para crear una nueva actividad"""
    pass


class ActividadUpdate(BaseModel):
    """Esquema para actualizar parcialmente una actividad"""
    id: Optional[int] = None
    tema: Optional[str] = None
    actividad: Optional[int] = None
    servicio_encargado: Optional[str] = None
    persona_responsable: Optional[Dict[str, PersonaResponsable]] = None
    tiempo_aproximado: Optional[str] = None
    fechas_a_desarrollar: Optional[str] = None
    modalidad: Optional[str] = field(default=None, min_length=1, max_length=2)
    estado: Optional[str] = field(default=None, min_length=1, max_length=2)
    detalles: Optional[DetallesActividad] = None
    metadatos: Optional[MetadatosActividad] = None

class ActividadOut(ActividadBase):
    id: int

    model_config = ConfigDict(from_attributes=True)