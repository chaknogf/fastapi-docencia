from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session as SQLAlchemySession

from app.apicore import CRUDBase, get_db
from app.database.security import get_current_user
from app.models.actividades import Subdireccion_Perteneciente_Model
from app.schemas.actividad import (
    SubdireccionPertenecienteCreate,
    SubdireccionPertenecienteOut,
    SubdireccionPertenecienteUpdate,
)

router = APIRouter(prefix="/subdireccion", tags=["subdireccion"])

crud = CRUDBase[
    Subdireccion_Perteneciente_Model,
    SubdireccionPertenecienteCreate,
    SubdireccionPertenecienteUpdate,
](Subdireccion_Perteneciente_Model)


@router.get("/", response_model=List[SubdireccionPertenecienteOut])
async def listar_subdirecciones(
    id: Optional[int] = Query(None),
    nombre: Optional[str] = Query(None),
    activo: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    db: SQLAlchemySession = Depends(get_db),
):
    try:
        query = db.query(Subdireccion_Perteneciente_Model).order_by(
            desc(Subdireccion_Perteneciente_Model.id)
        )
        if id is not None:
            query = query.filter(Subdireccion_Perteneciente_Model.id == id)
        if nombre is not None:
            query = query.filter(
                Subdireccion_Perteneciente_Model.nombre.ilike(f"%{nombre}%")
            )
        if activo is not None:
            query = query.filter(Subdireccion_Perteneciente_Model.activo == activo)
        return query.offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{subdireccion_id}", response_model=SubdireccionPertenecienteOut)
async def obtener_subdireccion(
    subdireccion_id: int,
    db: SQLAlchemySession = Depends(get_db),
):
    sub = crud.get_or_404(db, id=subdireccion_id)
    return sub


@router.post("/", response_model=SubdireccionPertenecienteOut, status_code=201)
async def crear_subdireccion(
    data: SubdireccionPertenecienteCreate,
    current_user: str = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db),
):
    try:
        return crud.create(db, obj_in=data)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{subdireccion_id}", response_model=SubdireccionPertenecienteOut)
async def actualizar_subdireccion(
    subdireccion_id: int,
    data: SubdireccionPertenecienteUpdate,
    current_user: str = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db),
):
    try:
        return crud.update(db, id=subdireccion_id, obj_in=data)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{subdireccion_id}")
async def eliminar_subdireccion(
    subdireccion_id: int,
    current_user: str = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db),
):
    try:
        crud.remove(db, id=subdireccion_id)
        return {"message": "Subdirección eliminada exitosamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
