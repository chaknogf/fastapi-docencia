from datetime import datetime
from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import desc, func, extract, Integer, cast

from app.apicore import get_db
from app.database.security import oauth2_scheme, get_current_user
from app.models.actividades import (
   Subdireccion_Perteneciente_Model,
   Servicio_Encargado_Model,
)
from app.schemas.actividad import (
    ServiciosEncargadoSchema,
    ServiciosEncargadoUpdate,
)

router = APIRouter(tags=["servicios_responsables"])


@router.get("/servicios_responsables/", response_model=List[ServiciosEncargadoUpdate])
async def listar_servicios(
    id: Optional[int] = Query(None),
    nombre: Optional[str] = Query(None),
    sub: Optional[int] = Query(None),
    activo: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        query = db.query(Servicio_Encargado_Model).order_by(desc(Servicio_Encargado_Model.id))
        if id:
            query = query.filter(Servicio_Encargado_Model.id == id)
        if nombre:
            query = query.filter(Servicio_Encargado_Model.nombre.ilike(f"%{nombre}%"))
        if sub:
            query = query.filter(Servicio_Encargado_Model.subdireccion_id == sub)
        if activo is not None:
            query = query.filter(Servicio_Encargado_Model.activo == activo)
        return query.offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/servicios_responsables/crear/", status_code=201)
async def crear_servicio_responsable(
    servicio: ServiciosEncargadoSchema,
    current_user: str = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        nuevo_servicio = Servicio_Encargado_Model(**servicio.model_dump())
        db.add(nuevo_servicio)
        db.commit()
        db.refresh(nuevo_servicio)
        return JSONResponse(status_code=200, content={"message": "created successfully"})
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": "Conflicto: este servicio ya existe o viola una restricción única."
            }
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Error interno al crear el servicio.",
                "details": str(e)
            }
        )


@router.put("/servicio_responsable/actualizar/{servicio_id}")
async def actualizar_servicio(
    servicio_id: int,
    servicio: ServiciosEncargadoUpdate,
    current_user: str = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        db_servicio = (
            db.query(Servicio_Encargado_Model)
            .filter(Servicio_Encargado_Model.id == servicio_id)
            .first()
        )
        if not db_servicio:
            raise HTTPException(
                status_code=404,
                detail={"status": "error", "message": "Servicio no encontrado"}
            )
        update_data = servicio.model_dump(exclude_unset=True)
        update_data.pop("id", None)
        update_data.pop("subdireccion", None)
        for key, value in update_data.items():
            setattr(db_servicio, key, value)
        db.commit()
        db.refresh(db_servicio)
        return {
            "status": "success",
            "message": "Servicio actualizado exitosamente",
            "data": {"id": db_servicio.id}
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Error interno al actualizar el servicio",
                "details": str(e)
            }
        )


@router.patch("/actividad/desactivar/{servicio_id}")
async def desactivar_servicio(
    servicio_id: int,
    current_user: str = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db)
):
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
