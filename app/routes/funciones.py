from datetime import datetime, date, timedelta
from typing import Optional, List, Tuple
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, asc

from app.database.db import get_db
from app.database.security import oauth2_scheme, get_current_admin_user
from app.config.mail_config import conf
from fastapi_mail import FastMail, MessageSchema, MessageType
from app.models.actividades import VistaActividad
from app.models.user import UserModel

router = APIRouter(tags=["actividades"])

DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]
ESTADO_COLOR = {
    "Programado": "#2563EB",
    "Reprogramado": "#D97706",
    "Realizado": "#16A34A",
    "Cancelado": "#DC2626",
    "Suspendido": "#EA580C",
}


def _generar_cuerpo_html(usuario: UserModel, mes_actual: int, db: SQLAlchemySession) -> Optional[str]:
    """
    Genera el cuerpo HTML del correo mensual de actividades.
    """
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


async def enviar_correos_mensuales_async(db: SQLAlchemySession) -> int:
    """
    Envía correos mensuales de forma asíncrona.
    """
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
            await fm.send_message(message)
            enviados += 1
        except Exception as e:
            print(f"Error enviando correo a {usuario.email}: {e}")

    return enviados


def enviar_correos_mensuales(db: SQLAlchemySession) -> int:
    """
    Versión síncrona para BackgroundTasks.
    """
    import asyncio

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Si ya hay un loop corriendo, crear una tarea
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                result = pool.submit(
                    asyncio.run,
                    enviar_correos_mensuales_async(db)
                )
                return result.result()
        else:
            return loop.run_until_complete(enviar_correos_mensuales_async(db))
    except RuntimeError:
        return asyncio.run(enviar_correos_mensuales_async(db))


# ======================================================
# CORREO SEMANAL DE ACTIVIDADES
# ======================================================

def _rango_semana_actual(fecha_referencia: Optional[date] = None) -> Tuple[date, date]:
    """
    Devuelve (lunes, domingo) de la semana actual.
    La semana inicia en lunes.
    """
    hoy = fecha_referencia or date.today()
    lunes = hoy - timedelta(days=hoy.weekday())
    domingo = lunes + timedelta(days=6)
    return lunes, domingo


def _formato_hora(horario) -> str:
    """Convierte horario (time) a formato HH:MM."""
    if not horario:
        return "Por definir"
    return horario.strftime("%H:%M")


def _estado_etiqueta(estado: Optional[str]) -> str:
    """Normaliza estado a etiqueta legible (acepta códigos o etiquetas)."""
    if not estado:
        return "Sin estado"
    mapa = {
        "P": "Programado",
        "R": "Realizado",
        "C": "Cancelado",
        "S": "Suspendido",
    }
    return mapa.get(estado.strip().upper(), estado.strip().capitalize() if estado else estado)


def _responsables_html(actividad: VistaActividad) -> str:
    """
    Extrae los nombres (y puestos) de persona_responsable (JSONB).
    Soporta tanto {nombre, puesto} directo como {r0: {...}, r1: {...}}.
    """
    try:
        data = actividad.persona_responsable or {}
        if isinstance(data, dict) and isinstance(data.get("nombre"), str) and data["nombre"]:
            lista = [data]
        elif isinstance(data, dict):
            lista = [v for v in data.values() if isinstance(v, dict)]
        elif isinstance(data, list):
            lista = [v for v in data if isinstance(v, dict)]
        else:
            lista = []
        nombres = []
        for v in lista:
            nombre = str(v.get("nombre", "")).strip()
            if not nombre:
                continue
            puesto = str(v.get("puesto", "")).strip()
            nombres.append(f"{nombre} · <em>{puesto}</em>" if puesto else nombre)
        return "<br>".join(nombres) if nombres else ""
    except Exception:
        return ""


def _fila_actividad_html(actividad: VistaActividad) -> str:
    """Fila de la tabla HTML para una actividad."""
    estado = _estado_etiqueta(actividad.estado)
    color_estado = ESTADO_COLOR.get(estado, "#6B7280")
    modalidad = (actividad.modalidad or "").strip()
    color_modalidad = "#7C3AED" if modalidad.lower() == "virtual" else "#0D9488"
    responsables = _responsables_html(actividad) or "—"
    lugar = (actividad.lugar or "Por definir").strip()

    return f"""
    <tr style="border-bottom: 1px solid #E5E7EB; vertical-align: top;">
        <td style="padding: 10px 12px; white-space: nowrap; font-weight: 700; color: #0F766E; font-size: 14px;">{_formato_hora(actividad.horario_programado)}</td>
        <td style="padding: 10px 12px; font-size: 14px; color: #111827;">{actividad.tema or ""}</td>
        <td style="padding: 10px 12px; text-align: center; white-space: nowrap;">
            <span style="display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; color: {color_modalidad}; background: {color_modalidad}14;">{modalidad or "—"}</span>
        </td>
        <td style="padding: 10px 12px; font-size: 13px; color: #4B5563; white-space: nowrap;">{lugar}</td>
        <td style="padding: 10px 12px; font-size: 13px; color: #4B5563;">{actividad.servicio_encargado or "—"}</td>
        <td style="padding: 10px 12px; font-size: 13px; color: #374151;">{responsables}</td>
        <td style="padding: 10px 12px; text-align: center; white-space: nowrap;">
            <span style="display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; color: {color_estado}; background: {color_estado}14;">{estado}</span>
        </td>
    </tr>"""


def _generar_cuerpo_html_semanal(db: SQLAlchemySession) -> Optional[str]:
    """
    Genera el cuerpo HTML (compartido) del correo con las actividades
    de la semana actual. Devuelve None si no hay actividades.
    """
    lunes, domingo = _rango_semana_actual()

    actividades = (
        db.query(VistaActividad)
        .filter(VistaActividad.fecha_programada >= lunes)
        .filter(VistaActividad.fecha_programada <= domingo)
        .order_by(asc(VistaActividad.fecha_programada), asc(VistaActividad.horario_programado))
        .all()
    )

    if not actividades:
        return None

    # Agrupar por día
    por_dia: dict[date, list[VistaActividad]] = {}
    for act in actividades:
        por_dia.setdefault(act.fecha_programada, []).append(act)

    rango_txt = (
        f"del {lunes.day} de {MESES_ES[lunes.month - 1]} "
        f"al {domingo.day} de {MESES_ES[domingo.month - 1]} de {domingo.year}"
    )

    dias_html = ""
    for fecha in sorted(por_dia.keys()):
        lista_dia = por_dia[fecha]
        dias_html += f"""
        <div style="margin: 24px 0;">
            <div style="display: flex; justify-content: space-between; align-items: baseline; border-left: 4px solid #0D9488; padding-left: 12px;">
                <h3 style="margin: 0; color: #0F172A; font-size: 16px;">{DIAS_ES[fecha.weekday()]} {fecha.day} de {MESES_ES[fecha.month - 1]}</h3>
                <span style="color: #6B7280; font-size: 13px;">{len(lista_dia)} actividad{'es' if len(lista_dia) != 1 else ''}</span>
            </div>
            <table cellpadding="0" cellspacing="0" style="border-collapse: collapse; width: 100%; margin-top: 10px;">
                <thead>
                    <tr style="background: #F1F5F9;">
                        <th style="text-align: left; padding: 8px 12px; font-size: 12px; text-transform: uppercase; color: #64748B;">Hora</th>
                        <th style="text-align: left; padding: 8px 12px; font-size: 12px; text-transform: uppercase; color: #64748B;">Tema</th>
                        <th style="text-align: center; padding: 8px 12px; font-size: 12px; text-transform: uppercase; color: #64748B;">Modalidad</th>
                        <th style="text-align: left; padding: 8px 12px; font-size: 12px; text-transform: uppercase; color: #64748B;">Lugar</th>
                        <th style="text-align: left; padding: 8px 12px; font-size: 12px; text-transform: uppercase; color: #64748B;">Servicio</th>
                        <th style="text-align: left; padding: 8px 12px; font-size: 12px; text-transform: uppercase; color: #64748B;">Responsables</th>
                        <th style="text-align: center; padding: 8px 12px; font-size: 12px; text-transform: uppercase; color: #64748B;">Estado</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(_fila_actividad_html(a) for a in lista_dia)}
                </tbody>
            </table>
        </div>"""

    total_actividades = len(actividades)
    total_dias = len(por_dia)

    return f"""
    <div style="background: #F8FAFC; padding: 20px 0; font-family: Arial, Helvetica, sans-serif; color: #333;">
        <div style="max-width: 760px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #0F766E, #134E4A); border-radius: 12px 12px 0 0; padding: 28px 32px; color: #FFFFFF;">
                <div style="font-size: 12px; letter-spacing: 2px; text-transform: uppercase; opacity: .8;">Hospital General Tipo I de Tecpán Guatemala</div>
                <h1 style="margin: 6px 0 0; font-size: 26px;">Cartelera de la semana</h1>
                <div style="margin-top: 8px; font-size: 14px; opacity: .92;">{rango_txt}</div>
            </div>
            <div style="background: #FFFFFF; border-radius: 0 0 12px 12px; box-shadow: 0 4px 16px rgba(0,0,0,.06); padding: 8px 32px 28px;">
                <div style="display: flex; gap: 12px; margin: 18px 0;">
                    <span style="background: #ECFDF5; color: #065F46; border-radius: 999px; padding: 6px 14px; font-size: 13px; font-weight: 700;">{total_actividades} actividades programadas</span>
                    <span style="background: #EFF6FF; color: #1D4ED8; border-radius: 999px; padding: 6px 14px; font-size: 13px; font-weight: 700;">{total_dias} días</span>
                </div>
                <p style="margin: 4px 0 0;">[[SALUDO]] Te compartimos las actividades programadas para esta semana. Consulta la cartelera en línea para más detalles y enlaces de acceso.</p>
                {dias_html}
                <div style="margin-top: 28px; border-top: 2px dashed #CBD5E1; padding-top: 16px; font-size: 12px; color: #64748B; text-align: center;">
                    <strong>Coordinación de Docencia</strong> · Hospital Tecpán<br>
                    Este correo es informativo. Si tienes dudas sobre alguna actividad, contacta al servicio responsable.
                </div>
            </div>
        </div>
    </div>"""


async def enviar_correos_semanales_async(db: SQLAlchemySession) -> int:
    """
    Envía a cada usuario registrado (activo) un correo con las actividades
    de la semana actual. Devuelve el número de correos enviados.
    """
    usuarios = (
        db.query(UserModel)
        .filter(UserModel.email.isnot(None))
        .filter(UserModel.estado == "A")
        .all()
    )

    if not usuarios:
        return 0

    cuerpo_base = _generar_cuerpo_html_semanal(db)
    if not cuerpo_base:
        return 0

    fm = FastMail(conf)
    enviados = 0

    for usuario in usuarios:
        cuerpo = cuerpo_base.replace(
            "[[SALUDO]]",
            f"Hola <strong>{usuario.nombre}</strong>,"
        )
        message = MessageSchema(
            subject=f"Actividades de la semana - {datetime.now().strftime('%B %Y')}",
            recipients=[usuario.email],
            body=cuerpo,
            subtype=MessageType.html,
        )
        try:
            await fm.send_message(message)
            enviados += 1
        except Exception as e:
            print(f"Error enviando correo semanal a {usuario.email}: {e}")

    return enviados


def enviar_correos_semanales(db: SQLAlchemySession) -> int:
    """
    Versión síncrona de enviar_correos_semanales_async para
    BackgroundTasks y el scheduler.
    """
    import asyncio

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                result = pool.submit(
                    asyncio.run,
                    enviar_correos_semanales_async(db)
                )
                return result.result()
        else:
            return loop.run_until_complete(enviar_correos_semanales_async(db))
    except RuntimeError:
        return asyncio.run(enviar_correos_semanales_async(db))


@router.post("/actividades/enviar-semanal")
async def enviar_actividades_semanales(
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_admin_user),
    db: SQLAlchemySession = Depends(get_db),
):
    """
    Programa el envío de correos semanales en segundo plano.
    Solo accesible para usuarios administradores.
    """
    try:
        background_tasks.add_task(enviar_correos_semanales, db)
        return {
            "mensaje": "Envío semanal de actividades programado en segundo plano"
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Error al programar envío semanal")


@router.post("/actividades/enviar-mensual")
async def enviar_actividades_mensuales(
    background_tasks: BackgroundTasks,
    db: SQLAlchemySession = Depends(get_db),
):
    """
    Programa el envío de correos mensuales en segundo plano.
    """
    try:
        background_tasks.add_task(enviar_correos_mensuales, db)
        return {"mensaje": "Envío de correos programado en segundo plano"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al programar envío")


@router.post("/verificador/")
async def validar_no_coincidan_actividades(
    fecha: str,
    hora: Optional[str] = Query(None),
    actividad_id: Optional[int] = Query(None),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Valida que no existan conflictos de horario para una actividad.
    """
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

    # Excluir lugares especiales (ej: virtual)
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
        "mensaje": "Existen actividades que coinciden en fecha u horario. Por favor programa otra fecha u hora.",
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
