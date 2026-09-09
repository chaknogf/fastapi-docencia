from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import asc, desc, func

from app.database.db import get_db
from app.database.security import get_current_user
from app.models.user import UserModel
from app.models.asistencia import Asistencia
from app.schemas.asistencia import AsistenciaCreate, AsistenciaBase, AsistenciaRead

# =========================
# ROUTER
# =========================
router = APIRouter(prefix="/asistencia", tags=["Asistencia"])


# =========================
# CREAR ASISTENCIA
# =========================
@router.post("/", response_model=AsistenciaRead)
async def registrar_asistencia(
    data: AsistenciaCreate,
    current_user: UserModel = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Registra una nueva asistencia vinculada a una capacitación (actividad).
    Requiere autenticación.
    """
    try:
        nueva = Asistencia(**data.model_dump())
        db.add(nueva)
        db.commit()
        db.refresh(nueva)
        return nueva

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al registrar asistencia")


# =========================
# LISTAR TODAS LAS ASISTENCIAS
# =========================
@router.get("/", response_model=List[AsistenciaRead])
async def listar_asistencias(
    capacitacion: Optional[int] = Query(None),
    fecha: Optional[str] = Query(None),
    fecha_desde: Optional[str] = Query(None, description="Fecha inicial (YYYY-MM-DD)"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha final (YYYY-MM-DD)"),
    db: SQLAlchemySession = Depends(get_db),
    orden: Optional[str] = Query("asc", description="Orden ascendente o descendente por fecha"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Devuelve la lista de asistencias registradas.
    Permite filtrado, ordenamiento y paginación.
    """
    try:
        query = db.query(Asistencia)

        if capacitacion:
            query = query.filter(Asistencia.capacitacion_id == capacitacion)
        if fecha:
            query = query.filter(func.date(Asistencia.fecha_registro) == fecha)
        if fecha_desde:
            query = query.filter(func.date(Asistencia.fecha_registro) >= fecha_desde)
        if fecha_hasta:
            query = query.filter(func.date(Asistencia.fecha_registro) <= fecha_hasta)

        query = query.order_by(
            desc(Asistencia.fecha_registro) if orden == "desc" else asc(Asistencia.fecha_registro)
        )

        return query.offset(skip).limit(limit).all()

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Error al obtener asistencias")


# =========================
# OBTENER ASISTENCIA POR ID
# =========================
@router.get("/{asistencia_id}", response_model=AsistenciaRead)
async def obtener_asistencia(
    asistencia_id: int,
    db: SQLAlchemySession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retorna un registro de asistencia específico.
    """
    asistencia = db.query(Asistencia).filter(Asistencia.id == asistencia_id).first()
    if not asistencia:
        raise HTTPException(status_code=404, detail="Registro de asistencia no encontrado")
    return asistencia


# =========================
# ACTUALIZAR ASISTENCIA
# =========================
@router.put("/{asistencia_id}", response_model=AsistenciaRead)
async def actualizar_asistencia(
    asistencia_id: int,
    data: AsistenciaBase,
    db: SQLAlchemySession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Actualiza los datos de una asistencia existente.
    """
    try:
        asistencia = db.query(Asistencia).filter(Asistencia.id == asistencia_id).first()
        if not asistencia:
            raise HTTPException(status_code=404, detail="Registro no encontrado")

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(asistencia, key, value)

        db.commit()
        db.refresh(asistencia)
        return asistencia

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar asistencia")


# =========================
# ELIMINAR ASISTENCIA
# =========================
@router.delete("/{asistencia_id}")
async def eliminar_asistencia(
    asistencia_id: int,
    db: SQLAlchemySession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Elimina un registro de asistencia por su ID.
    """
    try:
        asistencia = db.query(Asistencia).filter(Asistencia.id == asistencia_id).first()
        if not asistencia:
            raise HTTPException(status_code=404, detail="Registro no encontrado")

        db.delete(asistencia)
        db.commit()
        return {"message": "Asistencia eliminada correctamente"}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar asistencia")
