from datetime import datetime
from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import asc, desc, func, extract, Integer, cast
from app.config.mail_config import conf
from fastapi_mail import FastMail, MessageSchema, MessageType
from app.database.db import SessionLocal
from app.models.asistencia import Asistencia
from app.schemas.asistencia import AsistenciaCreate, AsistenciaBase, AsistenciaRead

# =========================
# ROUTER Y SEGURIDAD
# =========================
router = APIRouter(prefix="/asistencia", tags=["Asistencia"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# =========================
# DEPENDENCIA DE DB
# =========================
def get_db():
    """
    Genera y cierra la sesión de la base de datos por petición.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# CREAR ASISTENCIA
# =========================
@router.post("/", response_model=AsistenciaRead)
async def registrar_asistencia(
    data: AsistenciaCreate,
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Registra una nueva asistencia vinculada a una capacitación (actividad).
    """
    try:
        nueva = Asistencia(**data.model_dump())
        db.add(nueva)
        db.commit()
        db.refresh(nueva)
        return nueva

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en base de datos: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# =========================
# LISTAR TODAS LAS ASISTENCIAS
# =========================
@router.get("/", response_model=List[AsistenciaRead])
async def listar_asistencias(
    capacitacion: Optional[int] = Query(None),
    fecha: Optional[str] = Query(None),
    db: SQLAlchemySession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(50, le=200, description="Número máximo de registros a devolver"),
    orden: Optional[str] = Query("asc", description="Orden ascendente o descendente por fecha")
):
    """
    Devuelve la lista de asistencias registradas.
    Permite filtrado, paginación y ordenamiento.
    """
    try:
        query = db.query(Asistencia)

        if capacitacion:
            query = query.filter(Asistencia.capacitacion_id == capacitacion)
        if fecha:
            query = query.filter(func.date(Asistencia.fecha_registro) == fecha)

        query = query.order_by(desc(Asistencia.fecha_registro) if orden == "desc" else asc(Asistencia.fecha_registro))
        resultados = query.offset(skip).limit(limit).all()
        return resultados
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error en base de datos: {str(e)}")


# =========================
# OBTENER ASISTENCIA POR ID
# =========================
@router.get("/{asistencia_id}", response_model=AsistenciaRead)
async def obtener_asistencia(asistencia_id: int, db: SQLAlchemySession = Depends(get_db)):
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
    db: SQLAlchemySession = Depends(get_db)
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
        raise HTTPException(status_code=500, detail=f"Error al actualizar: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# =========================
# ELIMINAR ASISTENCIA
# =========================
@router.delete("/{asistencia_id}")
async def eliminar_asistencia(asistencia_id: int, db: SQLAlchemySession = Depends(get_db)):
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
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {str(e)}")