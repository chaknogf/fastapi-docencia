from datetime import datetime
from typing import Optional, List, Dict, Type
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, func, extract, Integer, cast

from app.database.db import SessionLocal
from app.models.actividades import (
   Modalidad,
   Actividad,
   Estado
)
from app.schemas.actividad import (
    ModalidadSchema,
    ModalidadCreate,
    EstadoCreate,
    EstadoSchema,
    TipoActividadCreate,
    TipoActividadSchema
    
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

def get_model_Actividad() -> Type[Actividad]:
    return Actividad
def get_model_Estado() -> Type[Estado]:
    return Estado
def get_model_Modalidad() -> Type[Modalidad]:
    return Modalidad
# =========================
# ENDPOINT: LISTAR TIPO DE ACTIVIDAD
# =========================
@router.get("/tipos_actividad/", response_model=List[TipoActividadSchema], tags=["tipo de actividad"])
async def listar_actividad(
    id: Optional[int] = Query(None),
    activo: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    token: str = Depends(oauth2_scheme),  # Requiere token
    db: SQLAlchemySession = Depends(get_db),
    model: Type[Actividad] = Depends(get_model_Actividad)
):
    try:
        query = db.query(model).order_by(desc(model.id))
        # Aplicar paginación
        return query.offset(skip).limit(limit).all()

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# ENDPOINT: CREAR ACTIVIDAD
# =========================
@router.post("/tipos_actividad/crear/", status_code=201, tags=["tipo de actividad"])
async def crear_tipo_actividad(
    schemadata: TipoActividadCreate,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db),
    model: Type[Actividad] = Depends(get_model_Actividad)
):
    try:
        # Crear instancia del modelo con los datos del schema
        data = model(**schemadata.model_dump())
        db.add(data)  # Agregar a sesión
        db.commit()              # Guardar cambios
        db.refresh(data)  # Refrescar para obtener ID generado
        return {"message": "Creado exitosamente", "id": data.id}

    except SQLAlchemyError as e:
        db.rollback()  # Deshacer cambios en caso de error
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# ENDPOINT: ACTUALIZAR ACTIVIDAD
# =========================
@router.put("/tipos_actividad/actualizar/{data_id}", tags=["tipo de actividad"])
async def actualizar_actividad(
    data_id: int,
    schemadata: TipoActividadSchema,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db),
    model: Type[Actividad] = Depends(get_model_Actividad)
):
    try:
        data = db.query(model).filter(model.id == data_id).first()
        if not data:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")
        # Actualiza solo los campos que se pasaron en el request
        for key, value in model.model_dump(exclude_unset=True).items():
            setattr(data, key, value)

        db.commit()
        db.refresh(data)
        return {"message": "Actualización Exitosa"}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# ENDPOINT: LISTAR MODALIDADES
# =========================
@router.get("/modalidades/", response_model=List[ModalidadSchema], tags=["modalidades"])
async def listar_modalidades(
    id: Optional[int] = Query(None),
    activo: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db),
    model: Type[Modalidad] = Depends(get_model_Modalidad)
):
    try:
        query = db.query(model).order_by(desc(model.id))

        if id is not None:
            query = query.filter(model.id == id)
        if activo is not None:
            query = query.filter(model.activo == activo)

        return query.offset(skip).limit(limit).all()

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
# =========================
# ENDPOINT: CREAR MODALIDAD
# =========================
@router.post("/modalidad/crear/", status_code=201, tags=["modalidades"])
async def crear_tipo_actividad(
    schemadata: ModalidadCreate,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db),
    model: Type[Modalidad] = Depends(get_model_Modalidad)
):
    try:
        # Crear instancia del modelo con los datos del schema
        data = model(**schemadata.model_dump())
        db.add(data)  # Agregar a sesión
        db.commit()              # Guardar cambios
        db.refresh(data)  # Refrescar para obtener ID generado
        return {"message": "Creado exitosamente", "id": data.id}

    except SQLAlchemyError as e:
        db.rollback()  # Deshacer cambios en caso de error
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# ENDPOINT: ACTUALIZAR MODALIDAD
# =========================
@router.put("/modalidad/actualizar/{data_id}", tags=["modalidades"])
async def actualizar_modalidad(
    data_id: int,
    schemadata: ModalidadSchema,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db),
    model: Type[Modalidad] = Depends(get_model_Modalidad)
):
    try:
        data = db.query(model).filter(model.id == data_id).first()
        if not data:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")
        # Actualiza solo los campos que se pasaron en el request
        for key, value in model.model_dump(exclude_unset=True).items():
            setattr(data, key, value)

        db.commit()
        db.refresh(data)
        return {"message": "Actualización Exitosa"}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    

# =========================
# ENDPOINT: LISTAR ESTADOS
# =========================
@router.get("/estados/", response_model=List[EstadoSchema], tags=["estados"])
async def listar_estados(
    id: Optional[int] = Query(None),
    activo: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db),
    model: Type[Estado] = Depends(get_model_Estado)
):
    try:
        query = db.query(model).order_by(desc(model.id))

        if id is not None:
            query = query.filter(model.id == id)
        if activo is not None:
            query = query.filter(model.activo == activo)

        return query.offset(skip).limit(limit).all()

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
# =========================
# ENDPOINT: CREAR ESTADO
# =========================
@router.post("/estado/crear/", status_code=201, tags=["estados"])
async def crear_estados(
    schemadata: EstadoCreate,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db),
    model: Type[Estado] = Depends(get_model_Estado)
):
    try:
        # Crear instancia del modelo con los datos del schema
        data = model(**schemadata.model_dump())
        db.add(data)  # Agregar a sesión
        db.commit()              # Guardar cambios
        db.refresh(data)  # Refrescar para obtener ID generado
        return {"message": "Creado exitosamente", "id": data.id}

    except SQLAlchemyError as e:
        db.rollback()  # Deshacer cambios en caso de error
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# ENDPOINT: ACTUALIZAR ACTIVIDAD
# =========================
@router.put("/estado/actualizar/{data_id}", tags=["estados"])
async def actualizar_estado(
    data_id: int,
    schemadata: EstadoSchema,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db),
    model: Type[Estado] = Depends(get_model_Estado)
):
    try:
        data = db.query(model).filter(model.id == data_id).first()
        if not data:
            raise HTTPException(status_code=404, detail="data no encontrada")
        # Actualiza solo los campos que se pasaron en el request
        for key, value in model.model_dump(exclude_unset=True).items():
            setattr(data, key, value)

        db.commit()
        db.refresh(data)
        return {"message": "Actualización Exitosa"}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))