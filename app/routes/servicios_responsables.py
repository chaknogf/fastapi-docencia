from datetime import datetime
from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, func, extract, Integer, cast

from app.database.db import SessionLocal
from app.models.actividades import (
   Subdireccion_Perteneciente_Model,
   Servicio_Encargado_Model,
)
from app.schemas.actividad import (
    ServiciosEncargadoSchema,
    ServiciosEncargadoUpdate,
    SubdireccionPertenecienteUpdate,
    SubdireccionPertenecienteSchema
)

# =========================
# ROUTER Y SEGURIDAD
# =========================
router = APIRouter()  # Instancia de APIRouter de FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # Seguridad OAuth2


# =========================
# DEPENDENCIA DE DB
# =========================
def get_db():
    """
    Genera y cierra la sesión de la base de datos por petición.
    Esto se usa en los endpoints con `Depends(get_db)`.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# ENDPOINT: LISTAR ACTIVIDADES
# =========================
@router.get("/servicios_responsables/", response_model=List[ServiciosEncargadoUpdate], tags=["servicios_responsables"])
async def listar_servicios(
    id: Optional[int] = Query(None),
    nombre: Optional[str] = Query(None),
    sub: Optional[int] = Query(None),
    activo: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    # token: str = Depends(oauth2_scheme),  # Requiere token
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Lista actividades filtrando por múltiples parámetros opcionales.
    Los filtros permiten búsquedas exactas o parciales.
    """
    try:
        # Query base de la vista completa de actividades
        query = db.query(Servicio_Encargado_Model).order_by(desc(Servicio_Encargado_Model.id))

        # Aplicar filtros condicionales si se pasan parámetros
        if id:
            query = query.filter(Servicio_Encargado_Model.id == id)
        if nombre:
            query = query.filter(Servicio_Encargado_Model.nombre.ilike(f"%{nombre}%"))
        if sub:
            query = query.filter(Servicio_Encargado_Model.subdireccion_id == sub)
        if activo:
            query = query.filter(Servicio_Encargado_Model.activo == activo)
        
        # Aplicar paginación
        return query.offset(skip).limit(limit).all()

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# ENDPOINT: CREAR ACTIVIDAD
# =========================
@router.post("/servicios_responsables/crear/", status_code=201, tags=["servicios_responsables"])
async def crear_servicio_responsable(
    servicio: ServiciosEncargadoSchema,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Crea una nuevo Servicio Responsable en la tabla `servicios_responsables`.
    """
    try:
        # Crear instancia del modelo con los datos del schema
        nuevo_servicio = Servicio_Encargado_Model(**servicio.model_dump())
        db.add(nuevo_servicio)  # Agregar a sesión
        db.commit()              # Guardar cambios
        db.refresh(nuevo_servicio)  # Refrescar para obtener ID generado
        return {"message": "Servicio creado exitosamente", "id": nuevo_servicio.id}

    except SQLAlchemyError as e:
        db.rollback()  # Deshacer cambios en caso de error
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# ENDPOINT: ACTUALIZAR ACTIVIDAD
# =========================
@router.put("/servicio_responsable/actualizar/{servicio_id}", tags=["servicios_responsables"])
async def actualizar_servicio(
    servicio_id: int,
    servicio: ServiciosEncargadoUpdate,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Actualiza un servicio existente. Solo actualiza los campos enviados.
    """
    try:
        db_actividad = db.query(Servicio_Encargado_Model).filter(Servicio_Encargado_Model.id == servicio_id).first()
        if not db_actividad:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")

        # Actualiza solo los campos que se pasaron en el request
        for key, value in Servicio_Encargado_Model.model_dump(exclude_unset=True).items():
            setattr(db_actividad, key, value)

        db.commit()
        db.refresh(db_actividad)
        return {"message": "Servicio actualizado exitosamente"}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# ENDPOINT: DESACTIVAR SERVICIO
# =========================
@router.patch("/actividad/desactivar/{servicio_id}", tags=["servicios_responsables"])
async def desactivar_servicio(
    servicio_id: int,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Desactiva el servicio responsable (no se elimina de la base de datos).
    """
    try:
        servicio = db.query(Servicio_Encargado_Model).filter(
            Servicio_Encargado_Model.id == servicio_id
        ).first()

        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")

        servicio.activo = False
        db.commit()
        db.refresh(servicio)

        return {"message": "Servicio desactivado exitosamente", "servicio_id": servicio.id}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al desactivar el servicio: {e}")

# =========================
# ENDPOINT: Subdirección
# =========================

@router.get("/subdireccion/", response_model=List[SubdireccionPertenecienteUpdate], tags=["servicios_responsables"])
async def listar_servicios(
    id: Optional[int] = Query(None),
    nombre: Optional[str] = Query(None),
    activo: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    # token: str = Depends(oauth2_scheme),  # Requiere token
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Lista actividades filtrando por múltiples parámetros opcionales.
    Los filtros permiten búsquedas exactas o parciales.
    """
    try:
        # Query base de la vista completa de actividades
        query = db.query(Subdireccion_Perteneciente_Model).order_by(desc(Subdireccion_Perteneciente_Model.id))

        # Aplicar filtros condicionales si se pasan parámetros
        if id:
            query = query.filter(Subdireccion_Perteneciente_Model.id == id)
        if nombre:
            query = query.filter(Subdireccion_Perteneciente_Model.nombre.ilike(f"%{nombre}%"))
        if activo:
            query = query.filter(Subdireccion_Perteneciente_Model.activo == activo)
        
        # Aplicar paginación
        return query.offset(skip).limit(limit).all()

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))