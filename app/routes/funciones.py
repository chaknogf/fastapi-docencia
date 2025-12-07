from datetime import datetime
from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from datetime import time
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import asc, desc, func, extract, Integer, cast
from app.config.mail_config import conf
from fastapi_mail import FastMail, MessageSchema, MessageType



from app.database.db import SessionLocal
from app.models.actividades import (
    VistaActividad
)
from app.schemas.actividad import (
    ActividadVista,
)
from app.models.user import (
    UserModel
)
from app.schemas.schemas import (
    UserResponse
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






@router.post("/actividades/enviar-mensual", tags=["actividades"])
async def enviar_actividades_mensuales(
    usuario_id: int,
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Envía un correo al usuario con las actividades del mes actual.
    Se divide entre las actividades de su servicio y las del resto.
    """
    try:
        # === Obtener usuario ===
        usuario = db.query(UserModel).filter(UserModel.id == usuario_id).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        servicio_id = usuario.servicio_id
        mes_actual = datetime.now().month

        # === Consultar actividades ===
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

        # === Generar cuerpo HTML del correo ===
        cuerpo_html = f"""
        <div style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #2c3e50;">📅 Actividades del mes de {datetime.now().strftime('%B')}</h2>
            <p>Hola <strong>{usuario.nombre}</strong>, aquí tienes las actividades programadas este mes:</p>

            <h3 style="color: #2980b9;">🧭 Actividades de tu servicio</h3>
            <ul>
                {''.join([
                    f"<li><strong>{a.tema}</strong> – {a.fecha_programada.strftime('%d/%m/%Y') if a.fecha_programada else 'Sin fecha'} – {a.estado or 'Sin estado'}</li>"
                    for a in actividades_servicio
                ]) or "<li>No hay actividades registradas</li>"}
            </ul>

            <h3 style="color: #7f8c8d;">🏛️ Actividades de otros servicios</h3>
            <ul>
                {''.join([
                    f"<li><strong>{a.tema}</strong> – {a.servicio_encargado or 'Sin servicio'} – {a.fecha_programada.strftime('%d/%m/%Y') if a.fecha_programada else 'Sin fecha'}</li>"
                    for a in actividades_otros
                ]) or "<li>No hay actividades registradas</li>"}
            </ul>

            <p style="margin-top: 20px;">Atentamente,<br><strong>Coordinación de Docencia</strong></p>
        </div>
        """

        # === Configurar correo con FastAPI-Mail ===
        message = MessageSchema(
            subject=f"Actividades programadas - {datetime.now().strftime('%B %Y')}",
            recipients=[usuario.email],
            body=cuerpo_html,
            subtype=MessageType.html
        )

    
        fm = FastMail(conf)
        await fm.send_message(message)

        return {"mensaje": f"Correo enviado correctamente a {usuario.email}"}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error en base de datos: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    
    

@router.post("/actividades/enviar-mensual-todos", tags=["actividades"])
async def enviar_actividades_mensuales_todos(
    background_tasks: BackgroundTasks,
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Envía correos personalizados a todos los usuarios con las actividades del mes actual.
    Cada usuario recibe solo sus actividades y las del resto.
    """
    try:
        usuarios = db.query(UserModel).filter(UserModel.email.isnot(None)).all()
        if not usuarios:
            raise HTTPException(status_code=404, detail="No hay usuarios con correo registrado")

        mes_actual = datetime.now().month
        fm = FastMail(conf)
        enviados = 0

        for usuario in usuarios:
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

            cuerpo_html = f"""
            <div style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #2c3e50;">📅 Actividades del mes de {datetime.now().strftime('%B')}</h2>
                <p>Hola <strong>{usuario.nombre}</strong>, aquí tienes las actividades programadas este mes:</p>

                <h3 style="color: #2980b9;">🧭 Actividades de tu servicio</h3>
                <ul>
                    {''.join([
                        f"<li><strong>{a.tema}</strong> – {a.fecha_programada.strftime('%d/%m/%Y') if a.fecha_programada else 'Sin fecha'} – {a.estado or 'Sin estado'}</li>"
                        for a in actividades_servicio
                    ]) or "<li>No hay actividades registradas</li>"}
                </ul>

                <h3 style="color: #7f8c8d;">🏛️ Actividades de otros servicios</h3>
                <ul>
                    {''.join([
                        f"<li><strong>{a.tema}</strong> – {a.servicio_encargado or 'Sin servicio'} – {a.fecha_programada.strftime('%d/%m/%Y') if a.fecha_programada else 'Sin fecha'}</li>"
                        for a in actividades_otros
                    ]) or "<li>No hay actividades registradas</li>"}
                </ul>

                <p style="margin-top: 20px;">Atentamente,<br><strong>Coordinación de Docencia</strong></p>
            </div>
            """

            message = MessageSchema(
                subject=f"Actividades programadas - {datetime.now().strftime('%B %Y')}",
                recipients=[usuario.email],
                body=cuerpo_html,
                subtype=MessageType.html
            )

            # Enviar en segundo plano para no bloquear
            background_tasks.add_task(fm.send_message, message)
            enviados += 1

        return {"mensaje": f"Correos programados para envío a {enviados} usuarios."}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error en base de datos: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    
    
    
@router.post("/verificador/", tags=["actividades"])
async def validar_no_coincidan_actividades(
    fecha: str,
    hora: Optional[time] = Query(None),
    actividad_id: Optional[int] = Query(None),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Verifica conflictos entre actividades. Devuelve:
    - valido: bool
    - mensaje: str
    - coincidencias: lista de conflictos (solo si valido = False)
    """

    # Validación de fecha
    try:
        fecha_convertida = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de fecha inválido. Usa YYYY-MM-DD."
        )

    # Base del query
    query = db.query(VistaActividad).filter(
        VistaActividad.fecha_programada == fecha_convertida
    )

    # Filtro por hora si aplica
    if hora is not None:
        query = query.filter(VistaActividad.horario_programado == hora)

    # Exclusión del lugar 3 (no verificable)
    query = query.filter(VistaActividad.lugar_id != 3)

    # Exclusión del propio registro si se está editando
    if actividad_id is not None:
        query = query.filter(VistaActividad.id != actividad_id)

    coincidencias = query.all()

    # Caso A: No hay conflictos
    if not coincidencias:
        return {
            "valido": True,
            "mensaje": "Sin conflictos. Puede registrar la actividad.",
            "coincidencias": []
        }

    # Caso B: Sí hay conflictos
    # Podrías afinar el mensaje si quieres más elegancia contextual.
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