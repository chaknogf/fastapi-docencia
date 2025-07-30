from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import desc, cast
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, List
from app.database.db import SessionLocal
from app.models.actividades import ActividadesModel, VistaReporte, VistaEjecucion, VistaEjecucionServicio
from app.schemas.actividad import ActividadBase, ActividadCreate, ActividadUpdate, ActividadOut, ReporteActividad, VistaEjecucionSchema, VistaEjecucionServicioSchema
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import func, extract, Integer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/actividades/", response_model=List[ActividadUpdate], tags=["actividades"])
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
    mes: Optional[int] = Query(None),
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
        if mes:
            query = query.filter(ActividadesModel.detalles.op('->>')('mes') == str(mes))
       
        result = query.offset(skip).limit(limit).all()
        return result
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/cartelera/{mes}", response_model=List[ActividadUpdate], tags=["actividades"])
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
    actividad: ActividadCreate,
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
    actividad: ActividadUpdate,
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


# Reportes



@router.get("/reporte/estadisticas/estado/{anio}/{mes}", tags=["reportes"])
async def estadisticas_estado_mes_anio(
    anio: int,
    mes: int,
    db: SQLAlchemySession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        # Extraer año desde metadatos.registro (cadena tipo fecha)
        resultados = db.query(
            ActividadesModel.estado,
            func.count(ActividadesModel.id).label("total")
        ).filter(
            ActividadesModel.detalles['mes'].astext.cast(Integer) == mes,
            extract('year', func.to_date(ActividadesModel.metadatos['registro'].astext, 'YYYY-MM-DD')) == anio
        ).group_by(ActividadesModel.estado).all()

        return [{"estado": estado, "total": total} for estado, total in resultados]

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al generar estadísticas: {e}")
    
    
@router.get("/reporte/vista", response_model=List[ReporteActividad], tags=["reportes"])
async def obtener_reporte_vista(
    mes: Optional[int] = Query(None, description="Número del mes (1-12)"),
    anio: Optional[int] = Query(None, description="Año (ej. 2025)"),
    db: SQLAlchemySession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        query = db.query(VistaReporte)

        if mes is not None:
            query = query.filter(VistaReporte.mes == mes)
        if anio is not None:
            query = query.filter(VistaReporte.anio == anio)

        reportes = query.all()

        if not reportes:
            raise HTTPException(status_code=404, detail="No se encontraron reportes para ese mes y año.")
        
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(reportes)
        )

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar la vista: {e}")
    
    
@router.get("/ejecucion", response_model=list[VistaEjecucionSchema])
def obtener_vista_ejecucion(
    anio: Optional[int] = Query(None, description="Año (ej. 2025)"),
    db: SQLAlchemySession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        if anio is None:
            anio = datetime.now().year
        
        resultados = db.query(VistaEjecucion).filter(VistaEjecucion.anio == anio).all()
        
        if not resultados:
            raise HTTPException(status_code=404, detail="No se encontraron datos para el año especificado.")
        
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(resultados)
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar la vista de ejecución: {e}")


@router.get("/ejecucion_servicio", response_model=list[VistaEjecucionServicioSchema])
def obtener_vista_ejecucion_servicio(
   anio: Optional[int] = Query(None, description="Año (ej. 2025)"),
    db: SQLAlchemySession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        if anio is None:
            anio = datetime.now().year
        
        resultados = db.query(VistaEjecucionServicio).filter(VistaEjecucionServicio.anio == anio).all()
        
        if not resultados:
            raise HTTPException(status_code=404, detail="No se encontraron datos para el año especificado.")
        
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(resultados)
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar la vista de ejecución por servicio: {e}")  