from typing import Optional, Dict, Any
from pydantic import BaseModel, Field as field, ConfigDict
from datetime import datetime, date

# =========================================================
# Esquema para Modalidad
# =========================================================
class ModalidadSchema(BaseModel):
    id: int
    nombre: str
    codigo: str
    model_config = ConfigDict(from_attributes=True)

class ModalidadCreate(BaseModel):
    nombre: str
    codigo: str
    model_config = ConfigDict(from_attributes=True)

# =========================================================
# Esquema para Estado
# =========================================================
class EstadoSchema(BaseModel):
    id: int
    nombre: str
    codigo: str
    model_config = ConfigDict(from_attributes=True)
    
class EstadoCreate(BaseModel):
    nombre: str
    codigo: str
    model_config = ConfigDict(from_attributes=True)
    
# =========================================================
#Esquema para Tipo de Actividad
# =========================================================
class TipoActividadSchema(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool
    model_config = ConfigDict(from_attributes=True)

class TipoActividadCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    activo: bool
    model_config = ConfigDict(from_attributes=True)

# =========================================================
# Subesquema para Subdirección
# =========================================================
class SubdireccionPertenecienteSchema(BaseModel):
    
    nombre: str                              # Nombre de la subdirección
    descripcion: Optional[str] = None        # Descripción opcional
    activo: bool                             # Estado activo/inactivo
    
    model_config = ConfigDict(from_attributes=True)

class SubdireccionPertenecienteUpdate(BaseModel):
    id: int
    nombre: str                              # Nombre de la subdirección
    descripcion: Optional[str] = None        # Descripción opcional
    activo: bool                             # Estado activo/inactivo
    
    model_config = ConfigDict(from_attributes=True)

# =========================================================
# Subesquema para Servicio Encargado
# =========================================================
class ServiciosEncargadoSchema(BaseModel):
    nombre: str                              # Nombre del servicio
    descripcion: Optional[str] = None        # Descripción opcional
    jefe_inmediato: Optional[str] = None   # Jefe inmediato del servicio
    encargado_servicio: Optional[str] = None # Encargado del servicio
    activo: bool
    subdireccion_id: int
    # Estado activo/inactivo
    subdireccion: Optional[SubdireccionPertenecienteSchema] = None  # Relación anidada
    
    model_config = ConfigDict(from_attributes=True)

class ServiciosEncargadoUpdate(BaseModel):
    id: int
    nombre: str                              # Nombre del servicio
    descripcion: Optional[str] = None        # Descripción opcional
    jefe_inmediato: Optional[str] = None   # Jefe inmediato del servicio
    encargado_servicio: Optional[str] = None # Encargado del servicio
    activo: bool
    subdireccion_id: int
    # Estado activo/inactivo
    subdireccion: Optional[SubdireccionPertenecienteSchema] = None  # Relación anidada
    
    model_config = ConfigDict(from_attributes=True)

# =========================================================
# Subesquema para Persona Responsable
# =========================================================
class PersonaResponsable(BaseModel):
    nombre: Optional[str] = field(default=None, description="Nombre del responsable")
    puesto: Optional[str] = field(default=None, description="Puesto o cargo del responsable")

# =========================================================
# Subesquema para Detalles de Actividad
# =========================================================
class DetallesActividad(BaseModel):
    link: Optional[str] = None
    duracion: Optional[str] = None
    grupo_dirigido: Optional[str] = None
    lugar: Optional[str] = None
    contenido: Optional[str] = None
    asistencia: Optional[int] = None
    inasistencia: Optional[int] = None
    excelente: Optional[int] = None
    bueno: Optional[int] = None
    regular: Optional[int] = None
    deficiente: Optional[int] = None
    fecha_entrega_informe: Optional[str] = None
    mes: Optional[int] = None
    nota: Optional[str] = None

# =========================================================
# Subesquema para Metadatos
# =========================================================
class MetadatosActividad(BaseModel):
    user: Optional[str] = None
    registro: Optional[str] = None

# =========================================================
# Schema base para creación de Actividad
# =========================================================
class ActividadBase(BaseModel):
    tema: str
    actividad_id: int
    servicio_id: int
    subdireccion_id: int
    modalidad_id: int
    estado_id: int
    mes_id: Optional[int] = None
    persona_responsable: Optional[Dict[str, "PersonaResponsable"]] = None
    detalles: Optional[Any] = None
    metadatos: Optional[Any] = None
    tiempo_aproximado: Optional[str] = None
    fecha_programada: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)

# =========================================================
# Schema para crear actividad
# =========================================================
class ActividadCreate(ActividadBase):
    """Schema para crear una nueva actividad"""
    pass

# =========================================================
# Schema para actualizar actividad
# =========================================================
class ActividadUpdate(BaseModel):
    """Schema para actualizar parcialmente una actividad"""
    id: Optional[int] = None
    tema: str
    actividad_id: int
    servicio_id: int
    subdireccion_id: int
    modalidad_id: int
    estado_id: int
    mes_id: Optional[int] = None
    persona_responsable: Optional[Dict[str, "PersonaResponsable"]] = None
    detalles: Optional["DetallesActividad"] = None
    metadatos: Optional["MetadatosActividad"] = None
    tiempo_aproximado: Optional[str] = None
    fecha_programada: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)

# =========================================================
# Schema para vistas completas de actividad
# =========================================================
class ActividadVista(BaseModel):
    id: int
    tema: str
    actividad: str
    actividad_id: int
    descripcion_actividad: Optional[str] = None

    subdireccion: Optional[str] = None
    subdireccion_id: Optional[int] = None
    servicio_encargado: Optional[str] = None
    servicio_id: Optional[int] = None

    persona_responsable: Optional[Dict[str, PersonaResponsable]] = None
    tiempo_aproximado: Optional[str] = None
    fecha_programada: Optional[date] = None  #
    mes: Optional[str] = None
    mes_id: Optional[int] = None
    anio: Optional[int] = None

    modalidad: Optional[str] = None
    modalidad_id: Optional[int] = None
    estado: Optional[str] = None
    estado_id: Optional[int] = None

    detalles: Optional[DetallesActividad] = None
    metadatos: Optional[MetadatosActividad] = None

    # ✅ Permite crear instancias desde ORM (SQLAlchemy)
    model_config = ConfigDict(from_attributes=True)


# =========================================================
# Schema de salida con ID
# =========================================================
class ActividadOut(ActividadBase):
    id: int

# =========================================================
# Schema para reportes resumidos
# =========================================================
class ReporteActividad(BaseModel):
    id: int
    tema: str
    actividad: str
    subdireccion: Optional[str] = None
    servicio_encargado: Optional[str] = None
    fecha_programada: Optional[date] = None
    mes: Optional[str] = None
    mes_id: Optional[int] = None
    anio: Optional[int] = None
    modalidad: Optional[str] = None
    estado: Optional[str] = None
    nota: Optional[str] = None
    encargado_servicio: Optional[str] = None
    jefe_inmediato: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# =========================================================
# Schema para vista de ejecución por estado
# =========================================================
class VistaEjecucionSchema(BaseModel):
    subdireccion_id: Optional[int] = None
    subdireccion: Optional[str] = None
    servicio_id: Optional[int] = None
    servicio_encargado: Optional[str] = None
    anio: Optional[int] = None
    completa: Optional[int] = None
    programada: Optional[int] = None
    reprogramada: Optional[int] = None
    suspendida: Optional[int] = None
    total: Optional[int] = None
    ejecutado: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
    
    
class ResumenAnualSchema(BaseModel):
    anio: Optional[int] = None
    programadas: Optional[int] = 0
    reprogramadas: Optional[int] = 0
    completadas: Optional[int] = 0
    anuladas: Optional[int] = 0
    total: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)
    
   