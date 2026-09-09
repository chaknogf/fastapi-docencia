from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import asc, desc

from app.database.db import get_db
from app.database.security import get_current_user, get_current_admin_user
from app.models.user import UserModel
from app.models.actividades import (
    ActividadesModel,
    ResumenAnualModel,
    VistaReporte,
    Vista_Ejecucion_Model,
    VistaActividad,
    Servicio_Encargado_Model,
)
from app.schemas.actividad import (
    ActividadBase,
    ActividadUpdate,
    ListaActividades,
    ReporteActividad,
    ResumenAnualSchema,
    VistaEjecucionSchema,
)

# =========================
# ROUTER
# =========================
router = APIRouter()


# =========================
# ENDPOINT: LISTAR ACTIVIDADES
# =========================
@router.get("/actividades/", response_model=ListaActividades, tags=["actividades"])
async def listar_actividades(
    id: Optional[int] = Query(None),
    tema: Optional[str] = Query(None),
    actividad: Optional[str] = Query(None),
    servicio_encargado: Optional[int] = Query(None, description="ID del servicio"),
    subdireccion_id: Optional[int] = Query(None, description="ID de la subdirección"),
    persona: Optional[str] = Query(None),
    fecha_desde: Optional[str] = Query(None, description="Fecha inicial (YYYY-MM-DD)"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha final (YYYY-MM-DD)"),
    fecha_programada: Optional[str] = Query(None, description="Fecha exacta (YYYY-MM-DD)"),
    modalidad: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    entrega: Optional[str] = Query(None),
    mes: Optional[int] = Query(None),
    anio: Optional[int] = Query(None, description="Año (ej. 2025)"),
    lugar_id: Optional[int] = Query(None, description="ID del lugar de realización"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Lista actividades con paginación y filtros opcionales.
    """
    try:
        query = db.query(VistaActividad)

        if id:
            query = query.filter(VistaActividad.id == id)
        if tema:
            query = query.filter(VistaActividad.tema.ilike(f"%{tema}%"))
        if actividad:
            query = query.filter(VistaActividad.actividad.ilike(f"%{actividad}%"))
        if servicio_encargado:
            query = query.filter(VistaActividad.servicio_id == servicio_encargado)
        if subdireccion_id:
            query = query.filter(VistaActividad.subdireccion_id == subdireccion_id)
        if persona:
            query = query.filter(
                VistaActividad.persona_responsable['r0']['nombre'].astext.ilike(f"%{persona}%")
            )
        if fecha_desde:
            query = query.filter(VistaActividad.fecha_programada >= fecha_desde)
        if fecha_hasta:
            query = query.filter(VistaActividad.fecha_programada <= fecha_hasta)
        if fecha_programada:
            query = query.filter(VistaActividad.fecha_programada == fecha_programada)
        if modalidad:
            query = query.filter(VistaActividad.modalidad == modalidad)
        if estado:
            query = query.filter(VistaActividad.estado == estado)
        if entrega:
            query = query.filter(
                VistaActividad.detalles['fecha_entrega_informe'].astext == entrega
            )
        if mes:
            query = query.filter(VistaActividad.mes_id == mes)
        if anio:
            query = query.filter(VistaActividad.anio == anio)
        if lugar_id:
            query = query.filter(VistaActividad.lugar_id == lugar_id)

        if mes is not None:
            query = query.order_by(asc(VistaActividad.fecha_programada))
        else:
            query = query.order_by(desc(VistaActividad.id))

        total = query.count()
        items = query.offset(skip).limit(limit).all()

        return ListaActividades(total=total, actividades=items)

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# =========================
# ENDPOINT: CREAR ACTIVIDAD
# =========================
@router.post(
    "/actividad/crear/",
    status_code=201,
    tags=["actividades"],
    dependencies=[Depends(get_current_user)]
)
async def crear_actividad(
    actividad: ActividadBase,
    current_user: UserModel = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Crea una nueva actividad en la tabla `actividades`.
    Requiere autenticación.
    """
    try:
        actividad_dict = actividad.model_dump()
        actividad_dict.pop("id", None)

        if actividad_dict.get("fecha_programada"):
            actividad_dict["mes_id"] = actividad_dict["fecha_programada"].month

        # Agregar metadatos del usuario
        if "metadatos" not in actividad_dict or actividad_dict["metadatos"] is None:
            actividad_dict["metadatos"] = {}
        actividad_dict["metadatos"]["user"] = current_user.username

        nueva_actividad = ActividadesModel(**actividad_dict)
        db.add(nueva_actividad)
        db.commit()
        db.refresh(nueva_actividad)

        return {"message": "Actividad creada exitosamente", "id": nueva_actividad.id}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear actividad")


# =========================
# ENDPOINT: ACTUALIZAR ACTIVIDAD
# =========================
@router.put("/actividad/actualizar/{actividad_id}", tags=["actividades"])
async def actualizar_actividad(
    actividad_id: int,
    actividad: ActividadUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Actualiza una actividad existente. Solo actualiza los campos enviados.
    """
    try:
        db_actividad = db.query(ActividadesModel).filter(ActividadesModel.id == actividad_id).first()
        if not db_actividad:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")

        # Verificar permisos: admin o dueño del servicio
        if current_user.role != "admin":
            if db_actividad.servicio_id != current_user.servicio_id:
                raise HTTPException(
                    status_code=403,
                    detail="No tiene permiso para actualizar esta actividad"
                )

        update_data = actividad.model_dump(exclude_unset=True)

        if update_data.get("fecha_programada"):
            update_data["mes_id"] = update_data["fecha_programada"].month

        for key, value in update_data.items():
            setattr(db_actividad, key, value)

        db.commit()
        db.refresh(db_actividad)
        return {"message": "Actividad actualizada exitosamente"}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar actividad")


# =========================
# ENDPOINT: ELIMINAR ACTIVIDAD
# =========================
@router.delete(
    "/actividad/eliminar/{actividad_id}",
    tags=["actividades"],
    dependencies=[Depends(get_current_admin_user)]
)
async def eliminar_actividad(
    actividad_id: int,
    current_user: UserModel = Depends(get_current_admin_user),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Elimina una actividad por su ID.
    Solo administradores pueden eliminar.
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
        raise HTTPException(status_code=500, detail="Error al eliminar actividad")


# =========================
# ENDPOINT: REPORTE DE ACTIVIDADES
# =========================
@router.get("/reporte/vista", response_model=List[ReporteActividad], tags=["reportes"])
async def reporte_vista(
    mes: Optional[int] = Query(None, description="Número del mes (1-12)"),
    anio: Optional[int] = Query(None, description="Año (ej. 2025)"),
    subId: Optional[int] = Query(None, description="ID de la subdirección"),
    servicioId: Optional[int] = Query(None, description='ID del servicio responsable'),
    db: SQLAlchemySession = Depends(get_db),
):
    """
    Retorna la lista de reportes resumidos filtrando opcionalmente por mes y año.
    """
    query = db.query(VistaReporte)
    if mes is not None:
        query = query.filter(VistaReporte.mes_id == mes)
    if anio is not None:
        query = query.filter(VistaReporte.anio == anio)
    if subId is not None:
        query = query.filter(VistaReporte.subdireccion_id == subId)
    if servicioId is not None:
        query = query.filter(VistaReporte.servicio_id == servicioId)
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
    Reporte de ejecución por subdirección, servicio y año.
    Incluye todos los servicios, incluso aquellos sin actividades (0 ejecución).
    """
    anio = anio or datetime.now().year

    servicios = (
        db.query(Servicio_Encargado_Model)
        .filter(Servicio_Encargado_Model.activo == True)
        .all()
    )
    if servicio_id:
        servicios = [s for s in servicios if s.id == servicio_id]

    ejecucion_por_servicio: dict = {}
    view_query = db.query(Vista_Ejecucion_Model).filter(
        Vista_Ejecucion_Model.anio == anio
    )
    if sub:
        view_query = view_query.filter(Vista_Ejecucion_Model.subdireccion_id == sub)
    if servicio_id:
        view_query = view_query.filter(Vista_Ejecucion_Model.servicio_id == servicio_id)
    if ejecutado is not None:
        view_query = view_query.filter(Vista_Ejecucion_Model.ejecutado > ejecutado)

    for row in view_query.all():
        ejecucion_por_servicio[row.servicio_id] = row

    resultados = []
    for s in servicios:
        if sub and (not s.subdireccion or s.subdireccion_id != sub):
            continue

        entry = ejecucion_por_servicio.get(s.id)
        resultados.append(
            VistaEjecucionSchema(
                servicio_id=s.id,
                servicio_encargado=s.nombre,
                subdireccion_id=s.subdireccion_id,
                subdireccion=s.subdireccion.nombre if s.subdireccion else None,
                anio=anio,
                completa=entry.completa if entry else 0,
                programada=entry.programada if entry else 0,
                reprogramada=entry.reprogramada if entry else 0,
                suspendida=entry.suspendida if entry else 0,
                total=entry.total if entry else 0,
                ejecutado=entry.ejecutado if entry else 0.0,
            )
        )

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
