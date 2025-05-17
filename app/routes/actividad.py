from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import desc, cast
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, List
from app.database.db import SessionLocal
from app.models.actividades import ActividadesModel
from app.schemas.actividad import ActividadBase
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/actividades/", response_model=List[ActividadBase], tags=["actividades"])
async def get_actividades(
    id: Optional[int] = Query(None),
    tema: Optional[str] = Query(None),
    actividad: Optional[int] = Query(None),
    service_encargado: Optional[str] = Query(None),
    persona: Optional[str] = Query(None),
    fecha: Optional[str] = Query(None),
    modalidad: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    entrega: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=0),
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        query = db.query(ActividadesModel).order_by(desc(ActividadesModel.id))

        if id:
            query = query.filter(ActividadesModel.id == id)
        if tema:
            query = query.filter(ActividadesModel.tema.ilike(f"%{tema}%"))
        if actividad:
            query = query.filter(ActividadesModel.actividad == actividad)
        if service_encargado:
            query = query.filter(ActividadesModel.service_encargado.ilike(f"%{service_encargado}%"))
        if persona:
            query = query.filter(ActividadesModel.persona_responsable.nombre.ilike(f"%{persona}%"))
        if fecha:
            query = query.filter(ActividadesModel.fechas_a_desarrollar.ilike(f"%{fecha}%"))
        if modalidad:
            query = query.filter(ActividadesModel.modalidad == modalidad)
        if estado:
            query = query.filter(ActividadesModel.estado == estado)
        if entrega:
            query = query.filter(ActividadesModel.detalles.fecha_entrega_informe == entrega)
       
        result = query.offset(skip).limit(limit).all()
        return result
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/cartelera/{mes}", response_model=List[ActividadBase], tags=["actividades"])
async def get_actividades(
    mes: int,  # <- Ya no es Optional ni Query
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        query = db.query(ActividadesModel).filter(
                ActividadesModel.detalles.op('->>')('mes') == str(mes)
            )
        return query.all()
    except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Error en consulta por mes: {e}")


@router.post("/actividad/crear/", status_code=201, tags=["actividades"])
async def create_actividad(
    actividad: ActividadBase,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        new_actividad = ActividadesModel(**actividad.model_dump())
        db.add(new_actividad)
        db.commit()
        return JSONResponse(status_code=201, content={"message": "Actividad creado exitosamente", "id": new_actividad.id})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/actividad/actualizar/{actividad_id}", tags=["actividades"])
async def update_actividad(
    actividad_id: int,
    actividad: ActividadBase,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        db_actividad = db.query(ActividadesModel).filter(ActividadesModel.id == actividad_id).first()
        if not db_actividad:
            raise HTTPException(status_code=404, detail="Actividad no encontrado")

        update_data = actividad.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_actividad, key, value)

        db.commit()
        return JSONResponse(status_code=200, content={"message": "Actividad actualizado exitosamente"})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/actividad/eliminar/{actividad_id}", tags=["actividades"])
async def delete_actividad(
    actividad_id: int,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        db_actividad = db.query(ActividadesModel).filter(ActividadesModel.id == actividad_id).first()
        if not db_actividad:
            raise HTTPException(status_code=404, detail="Actividad no encontrado")

        db.delete(db_actividad)
        db.commit()
        return JSONResponse(status_code=200, content={"message": "Actividad eliminado exitosamente"})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
