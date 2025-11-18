from typing import Optional, Dict, Any
from pydantic import BaseModel, Field as field, ConfigDict
from datetime import datetime, date, time

from sqlalchemy import Time

# =========================================================
# Esquema para Lugares
# =========================================================
class LugaresSchema(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class LugaresUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    
# =========================================================
# Esquema para Grupo de Edad
# =========================================================
class GrupoEdadSchema(BaseModel):
    id: int
    rango: str
    
    model_config = ConfigDict(from_attributes=True)

class GrupoEdadUpdate(BaseModel):
    rango: str
    
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