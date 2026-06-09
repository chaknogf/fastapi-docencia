from datetime import datetime
from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from datetime import time
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import asc, desc, func, extract, Integer, cast
from app.config.mail_config import conf
from fastapi_mail import FastMail, MessageSchema, MessageType

from app.database.db import SessionLocal
from app.database.security import oauth2_scheme
from app.models.actividades import VistaActividad
from app.schemas.actividad import ActividadVista
from app.models.user import UserModel
from app.schemas.schemas import UserResponse

router = APIRouter(tags=["actividades"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _generar_cuerpo_html(usuario: UserModel, mes_actual: int, db: SQLAlchemySession) -> Optional[str]:
    servicio_id = usuario.servicio_id

    actividades_servicio = (
        db.query(VistaActividad)
        .filter(VistaActividad.mes_id == mes_actual)
        .filter(VistaActividad.servicio_id == servicio_id)
        .order_by(desc(VistaActividad.fecha_programada))
        .all()
    )

    actividades_otros = (
        db.query(VistaActividad)
        .filter(VistaActividad.mes_id == mes_actual)
        .filter(VistaActividad.servicio_id != servicio_id)
        .order_by(desc(VistaActividad.fecha_programada))
        .all()
    )

    if not actividades_servicio and not actividades_otros:
        return None

    nombre_mes = datetime.now().strftime("%B").capitalize()

    return f"""
    <div style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #2c3e50;">Actividades del mes de {nombre_mes}</h2>
        <p>Hola <strong>{usuario.nombre}</strong>, aquí tienes las actividades programadas este mes:</p>

        <h3 style="color: #2980b9;">Actividades de tu servicio</h3>
        <ul>
            {''.join([
                f"<li><strong>{a.tema}</strong> – {a.fecha_programada.strftime('%d/%m/%Y') if a.fecha_programada else 'Sin fecha'} – {a.estado or 'Sin estado'}</li>"
                for a in actividades_servicio
            ]) or "<li>No hay actividades registradas</li>"}
        </ul>

        <h3 style="color: #7f8c8d;">Actividades de otros servicios</h3>
        <ul>
            {''.join([
                f"<li><strong>{a.tema}</strong> – {a.servicio_encargado or 'Sin servicio'} – {a.fecha_programada.strftime('%d/%m/%Y') if a.fecha_programada else 'Sin fecha'}</li>"
                for a in actividades_otros
            ]) or "<li>No hay actividades registradas</li>"}
        </ul>

        <p style="margin-top: 20px;">Atentamente,<br><strong>Coordinación de Docencia</strong></p>
    </div>
    """


def enviar_correos_mensuales(db: SQLAlchemySession) -> int:
    usuarios = db.query(UserModel).filter(UserModel.email.isnot(None)).all()
    mes_actual = datetime.now().month
    enviados = 0

    fm = FastMail(conf)

    for usuario in usuarios:
        cuerpo = _generar_cuerpo_html(usuario, mes_actual, db)
        if not cuerpo:
            continue

        message = MessageSchema(
            subject=f"Actividades programadas - {datetime.now().strftime('%B %Y')}",
            recipients=[usuario.email],
            body=cuerpo,
            subtype=MessageType.html,
        )

        try:
            fm.send_message(message)
            enviados += 1
        except Exception as e:
            print(f"Error enviando correo a {usuario.email}: {e}")

    return enviados


@router.post("/actividades/enviar-mensual")
async def enviar_actividades_mensuales(
    background_tasks: BackgroundTasks,
    db: SQLAlchemySession = Depends(get_db),
):
    try:
        background_tasks.add_task(enviar_correos_mensuales, db)
        return {"mensaje": "Envío de correos programado en segundo plano"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/verificador/")
async def validar_no_coincidan_actividades(
    fecha: str,
    hora: Optional[time] = Query(None),
    actividad_id: Optional[int] = Query(None),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        fecha_convertida = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de fecha inválido. Usa YYYY-MM-DD."
        )

    query = db.query(VistaActividad).filter(
        VistaActividad.fecha_programada == fecha_convertida
    )

    if hora is not None:
        query = query.filter(VistaActividad.horario_programado == hora)

    query = query.filter(VistaActividad.lugar_id != 3)

    if actividad_id is not None:
        query = query.filter(VistaActividad.id != actividad_id)

    coincidencias = query.all()

    if not coincidencias:
        return {
            "valido": True,
            "mensaje": "Sin conflictos. Puede registrar la actividad.",
            "coincidencias": []
        }

    return {
        "valido": False,
        "mensaje": "Existen actividades que coinciden en fecha u horario. Porfavor programa otra fecha u hora.",
        "coincidencias": [
            {
                "id": c.id,
                "tema": c.tema,
                "hora": str(c.horario_programado),
                "lugar": c.lugar,
                "servicio": c.servicio_encargado
            }
            for c in coincidencias
        ]
    }
