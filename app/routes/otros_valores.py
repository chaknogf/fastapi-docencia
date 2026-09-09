from typing import Optional, List, Type
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc

from app.database.db import get_db
from app.database.security import get_current_user
from app.models.user import UserModel
from app.models.actividades import (
    Modalidad,
    Actividad,
    Estado,
    LugaresModel,
    GrupoEdadModel
)
from app.schemas.actividad import (
    ModalidadSchema,
    ModalidadCreate,
    EstadoCreate,
    EstadoSchema,
    TipoActividadCreate,
    TipoActividadSchema,
)
from app.schemas.otras import (
    LugaresSchema,
    LugaresCreate,
    LugaresUpdate,
    GrupoEdadSchema,
    GrupoEdadUpdate
)

router = APIRouter()


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
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: SQLAlchemySession = Depends(get_db),
):
    try:
        query = db.query(Actividad).order_by(desc(Actividad.id))
        return query.offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Error al obtener tipos de actividad")


# =========================
# ENDPOINT: CREAR TIPO DE ACTIVIDAD
# =========================
@router.post(
    "/tipos_actividad/crear/",
    status_code=201,
    tags=["tipo de actividad"],
    dependencies=[Depends(get_current_user)]
)
async def crear_tipo_actividad(
    schemadata: TipoActividadCreate,
    current_user: UserModel = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db),
):
    try:
        data = Actividad(**schemadata.model_dump())
        db.add(data)
        db.commit()
        db.refresh(data)
        return {"message": "Creado exitosamente", "id": data.id}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear tipo de actividad")


# =========================
# ENDPOINT: ACTUALIZAR TIPO DE ACTIVIDAD
# =========================
@router.put(
    "/tipos_actividad/actualizar/{data_id}",
    tags=["tipo de actividad"],
    dependencies=[Depends(get_current_user)]
)
async def actualizar_tipo_actividad(
    data_id: int,
    schemadata: TipoActividadSchema,
    current_user: UserModel = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db),
):
    try:
        data = db.query(Actividad).filter(Actividad.id == data_id).first()
        if not data:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")

        for key, value in schemadata.model_dump(exclude_unset=True).items():
            setattr(data, key, value)

        db.commit()
        db.refresh(data)
        return {"message": "Actualización exitosa"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar")


# =========================
# ENDPOINT: LISTAR MODALIDADES
# =========================
@router.get("/modalidades/", response_model=List[ModalidadSchema], tags=["modalidades"])
async def listar_modalidades(
    id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: SQLAlchemySession = Depends(get_db),
):
    try:
        query = db.query(Modalidad).order_by(desc(Modalidad.id))
        if id is not None:
            query = query.filter(Modalidad.id == id)
        return query.offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Error al obtener modalidades")


# =========================
# ENDPOINT: CREAR MODALIDAD
# =========================
@router.post(
    "/modalidad/crear/",
    status_code=201,
    tags=["modalidades"],
    dependencies=[Depends(get_current_user)]
)
async def crear_modalidad(
    schemadata: ModalidadCreate,
    current_user: UserModel = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db),
):
    try:
        data = Modalidad(**schemadata.model_dump())
        db.add(data)
        db.commit()
        db.refresh(data)
        return {"message": "Creado exitosamente", "id": data.id}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear modalidad")


# =========================
# ENDPOINT: ACTUALIZAR MODALIDAD
# =========================
@router.put(
    "/modalidad/actualizar/{data_id}",
    tags=["modalidades"],
    dependencies=[Depends(get_current_user)]
)
async def actualizar_modalidad(
    data_id: int,
    schemadata: ModalidadSchema,
    current_user: UserModel = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db),
):
    try:
        data = db.query(Modalidad).filter(Modalidad.id == data_id).first()
        if not data:
            raise HTTPException(status_code=404, detail="Modalidad no encontrada")

        for key, value in schemadata.model_dump(exclude_unset=True).items():
            setattr(data, key, value)

        db.commit()
        db.refresh(data)
        return {"message": "Actualización exitosa"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar modalidad")


# =========================
# ENDPOINT: LISTAR ESTADOS
# =========================
@router.get("/estados/", response_model=List[EstadoSchema], tags=["estados"])
async def listar_estados(
    id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: SQLAlchemySession = Depends(get_db),
):
    try:
        query = db.query(Estado).order_by(desc(Estado.id))
        if id is not None:
            query = query.filter(Estado.id == id)
        return query.offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Error al obtener estados")


# =========================
# ENDPOINT: CREAR ESTADO
# =========================
@router.post(
    "/estado/crear/",
    status_code=201,
    tags=["estados"],
    dependencies=[Depends(get_current_user)]
)
async def crear_estado(
    schemadata: EstadoCreate,
    current_user: UserModel = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db),
):
    try:
        data = Estado(**schemadata.model_dump())
        db.add(data)
        db.commit()
        db.refresh(data)
        return {"message": "Creado exitosamente", "id": data.id}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear estado")


# =========================
# ENDPOINT: ACTUALIZAR ESTADO
# =========================
@router.put(
    "/estado/actualizar/{data_id}",
    tags=["estados"],
    dependencies=[Depends(get_current_user)]
)
async def actualizar_estado(
    data_id: int,
    schemadata: EstadoSchema,
    current_user: UserModel = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db),
):
    try:
        data = db.query(Estado).filter(Estado.id == data_id).first()
        if not data:
            raise HTTPException(status_code=404, detail="Estado no encontrado")

        for key, value in schemadata.model_dump(exclude_unset=True).items():
            setattr(data, key, value)

        db.commit()
        db.refresh(data)
        return {"message": "Actualización exitosa"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar estado")


# =========================
# ENDPOINT: LISTAR LUGARES
# =========================
@router.get("/lugareRealizacion/", response_model=List[LugaresSchema], tags=["otros"])
async def listar_lugares(
    id: Optional[int] = Query(None),
    db: SQLAlchemySession = Depends(get_db),
):
    try:
        query = db.query(LugaresModel)
        if id is not None:
            query = query.filter(LugaresModel.id == id)
        return query.order_by(desc(LugaresModel.id)).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Error al obtener lugares")


# =========================
# ENDPOINT: CREAR LUGAR
# =========================
@router.post(
    "/lugareRealizacion/",
    status_code=201,
    tags=["otros"],
    dependencies=[Depends(get_current_user)]
)
async def crear_lugar(
    data: LugaresCreate,
    current_user: UserModel = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db),
):
    try:
        lugar = LugaresModel(**data.model_dump())
        db.add(lugar)
        db.commit()
        db.refresh(lugar)
        return lugar
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear lugar")


# =========================
# ENDPOINT: ACTUALIZAR LUGAR
# =========================
@router.put(
    "/lugareRealizacion/{lugar_id}",
    response_model=LugaresSchema,
    tags=["otros"],
    dependencies=[Depends(get_current_user)]
)
async def actualizar_lugar(
    lugar_id: int,
    data: LugaresUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db),
):
    try:
        lugar = db.query(LugaresModel).filter(LugaresModel.id == lugar_id).first()
        if not lugar:
            raise HTTPException(status_code=404, detail="Lugar no encontrado")

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(lugar, key, value)

        db.commit()
        db.refresh(lugar)
        return lugar
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar lugar")


# =========================
# ENDPOINT: ELIMINAR LUGAR
# =========================
@router.delete(
    "/lugareRealizacion/{lugar_id}",
    tags=["otros"],
    dependencies=[Depends(get_current_user)]
)
async def eliminar_lugar(
    lugar_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db),
):
    try:
        lugar = db.query(LugaresModel).filter(LugaresModel.id == lugar_id).first()
        if not lugar:
            raise HTTPException(status_code=404, detail="Lugar no encontrado")

        db.delete(lugar)
        db.commit()
        return {"message": "Lugar eliminado exitosamente"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar lugar")


# =========================
# ENDPOINT: LISTAR GRUPOS DE EDAD
# =========================
@router.get("/gruposEdad/", response_model=List[GrupoEdadSchema], tags=["otros"])
async def listar_grupos_de_edad(
    id: Optional[int] = Query(None),
    db: SQLAlchemySession = Depends(get_db),
):
    try:
        query = db.query(GrupoEdadModel)
        if id is not None:
            query = query.filter(GrupoEdadModel.id == id)
        return query.order_by(desc(GrupoEdadModel.id)).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Error al obtener grupos de edad")
