from datetime import datetime
from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import asc, desc, func, extract, Integer, cast


from app.database.db import SessionLocal
from app.models.actividades import (
    ActividadesModel,
    ResumenAnualModel,
    VistaReporte,
    Vista_Ejecucion_Model,
    Vista_Ejecucion_Model,
    VistaActividad
)
from app.schemas.actividad import (
    ActividadBase,
    ActividadCreate,
    ActividadUpdate,
    ActividadVista,
    ReporteActividad,
    ResumenAnualSchema,
    VistaEjecucionSchema,
   
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
@router.get("/actividades/", response_model=List[ActividadVista], tags=["actividades"])
async def listar_actividades(
    id: Optional[int] = Query(None),
    tema: Optional[str] = Query(None),
    actividad: Optional[str] = Query(None),
    servicio_encargado: Optional[str] = Query(None),
    persona: Optional[str] = Query(None),
    fecha: Optional[str] = Query(None),
    modalidad: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    entrega: Optional[str] = Query(None),
    mes: Optional[int] = Query(None),
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
        query = db.query(VistaActividad).order_by(desc(VistaActividad.id))

        # Aplicar filtros condicionales si se pasan parámetros
        if id:
            query = query.filter(VistaActividad.id == id)
        if tema:
            query = query.filter(VistaActividad.tema.ilike(f"%{tema}%"))
        if actividad:
            query = query.filter(VistaActividad.actividad.ilike(f"%{actividad}%"))
        if servicio_encargado:
            query = query.filter(VistaActividad.servicio_id == servicio_encargado)
        if persona:
            # Filtro JSON: nombre del responsable dentro de persona_responsable
            query = query.filter(VistaActividad.persona_responsable['r0']['nombre'].astext.ilike(f"%{persona}%"))
        if fecha:
            query = query.filter(VistaActividad.fecha_programada == fecha)
        if modalidad:
            query = query.filter(VistaActividad.modalidad == modalidad)
        if estado:
            query = query.filter(VistaActividad.estado == estado)
        if entrega:
            query = query.filter(VistaActividad.detalles['fecha_entrega_informe'].astext == entrega)
        if mes:
            query = query.filter(VistaActividad.mes_id == mes)

        # Aplicar paginación
        return query.offset(skip).limit(limit).all()

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# ENDPOINT: CREAR ACTIVIDAD
# =========================
@router.post("/actividad/crear/", status_code=201, tags=["actividades"])
async def crear_actividad(
    actividad: ActividadBase, 
    # token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Crea una nueva actividad en la tabla `actividades`.
    """
    try:
        # Convertimos el schema a diccionario
        actividad_dict = actividad.model_dump()

        # 🔹 Eliminamos 'id' si existe para evitar conflicto con autoincrement
        actividad_dict.pop("id", None)

        # Crear instancia del modelo con los datos del schema
        nueva_actividad = ActividadesModel(**actividad_dict)

        db.add(nueva_actividad)       # Agregar a sesión
        db.commit()                   # Guardar cambios
        db.refresh(nueva_actividad)   # Refrescar para obtener ID generado

        return {"message": "Actividad creada exitosamente", "id": nueva_actividad.id}

    except SQLAlchemyError as e:
        db.rollback()  # Deshacer cambios en caso de error
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# ENDPOINT: ACTUALIZAR ACTIVIDAD
# =========================
@router.put("/actividad/actualizar/{actividad_id}", tags=["actividades"])
async def actualizar_actividad(
    actividad_id: int,
    actividad: ActividadUpdate,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Actualiza una actividad existente. Solo actualiza los campos enviados.
    """
    try:
        db_actividad = db.query(ActividadesModel).filter(ActividadesModel.id == actividad_id).first()
        if not db_actividad:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")

        # Actualiza solo los campos que se pasaron en el request
        for key, value in actividad.model_dump(exclude_unset=True).items():
            setattr(db_actividad, key, value)

        db.commit()
        db.refresh(db_actividad)
        return {"message": "Actividad actualizada exitosamente"}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# ENDPOINT: ELIMINAR ACTIVIDAD
# =========================
@router.delete("/actividad/eliminar/{actividad_id}", tags=["actividades"])
async def eliminar_actividad(
    actividad_id: int,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Elimina una actividad por su ID.
    """
    try:
        db_actividad = db.query(ActividadesModel).filter(ActividadesModel.id == actividad_id).first()
        if not db_actividad:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")

        db.delete(db_actividad)
        db.commit()
        return {"message": "Actividad eliminada exitosamente"}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# ENDPOINT: REPORTE DE ACTIVIDADES
# =========================
@router.get("/reporte/vista", response_model=List[ReporteActividad], tags=["reportes"])
async def reporte_vista(
    mes: Optional[int] = Query(None, description="Número del mes (1-12)"),
    anio: Optional[int] = Query(None, description="Año (ej. 2025)"),
    subdireccion: Optional[str] = Query(None, description="ID de la subdirección"),
    db: SQLAlchemySession = Depends(get_db),
    # token: str = Depends(oauth2_scheme)
):
    """
    Retorna la lista de reportes resumidos filtrando opcionalmente por mes y año.
    """
    query = db.query(VistaReporte)
    if mes is not None:
        query = query.filter(VistaReporte.mes_id == mes)
    if anio is not None:
        query = query.filter(VistaReporte.anio == anio)
    if subdireccion is not None:
        query = query.filter(VistaReporte.subdireccion == subdireccion)
    reportes = query.all()
    
    if not reportes:
        raise HTTPException(status_code=404, detail="No se encontraron reportes.")
    
    return reportes


# =========================
# ENDPOINT: VISTA DE EJECUCIÓN POR ESTADO
# =========================
@router.get(
    "/reporte/ejecucion",
    response_model=List[VistaEjecucionSchema],
    tags=["reportes"]
)
async def reporte_ejecucion(
    sub: int | None = Query(None),
    servicio_id: int | None = Query(None),
    anio: int | None = Query(None),
    ejecutado: float | None = Query(None),
    db: SQLAlchemySession = Depends(get_db),
):
    """
    Reporte de ejecución agrupado por subdirección, servicio y año.
    Permite filtrar opcionalmente por subdirección, servicio o año.
    """
    query = db.query(Vista_Ejecucion_Model)

    if sub:
        query = query.filter(Vista_Ejecucion_Model.subdireccion_id == sub)
    if servicio_id:
        query = query.filter(Vista_Ejecucion_Model.servicio_id == servicio_id)
    if anio:
        query = query.filter(Vista_Ejecucion_Model.anio == anio)
    if ejecutado is not None:
        query = query.filter(Vista_Ejecucion_Model.ejecutado > ejecutado)

    resultados = query.order_by(
        desc(Vista_Ejecucion_Model.anio),
        asc(Vista_Ejecucion_Model.subdireccion_id),
        asc(Vista_Ejecucion_Model.servicio_id)
    ).all()

    if not resultados:
        raise HTTPException(status_code=404, detail="No se encontraron resultados de ejecución")

    return resultados

@router.get("/reporte/resumen-anual", response_model=List[ResumenAnualSchema], tags=["reportes"])
async def reporte_resumen_anual(
    anio: Optional[int] = None,
    db: SQLAlchemySession = Depends(get_db)
):
    query = db.query(ResumenAnualModel)
    
    if anio is not None:
        query = query.filter(ResumenAnualModel.anio == anio)

    return query.order_by(ResumenAnualModel.anio.desc()).all()