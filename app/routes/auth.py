# app/routes/auth.py
"""
Endpoints de autenticación social (email magic link).
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.database.db import get_db
from app.database.security import create_access_token
from app.models.user import UserModel
from app.config.mail_config import conf
from app.core.rate_limiting import limiter, AUTH_RATE_LIMIT
from fastapi_mail import FastMail, MessageSchema, MessageType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


async def send_welcome_email(email: str, nombre: str, username: str):
    """Envía correo de bienvenida al nuevo usuario."""
    try:
        message = MessageSchema(
            subject="Bienvenido a Docencia Tecpán",
            recipients=[email],
            body=f"""
            <div style="font-family: Arial, sans-serif;">
                <h2>¡Hola {nombre}!</h2>
                <p>Tu cuenta ha sido creada exitosamente.</p>
                <p><b>Usuario:</b> {username}</p>
                <p><b>Correo:</b> {email}</p>
                <p>Ingresa al sistema para configurar tu contraseña.</p>
            </div>
            """,
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        logger.error(f"Error enviando correo de bienvenida: {e}")


@router.post("/email")
@limiter.limit(AUTH_RATE_LIMIT)
async def auth_email(
    request: Request,
    payload: dict,
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Autenticación mágica por email.
    Si el usuario no existe, lo crea automáticamente.
    """
    email = payload.get("email")
    nombre = payload.get("nombre", email.split("@")[0]) if email else None

    if not email:
        raise HTTPException(status_code=400, detail="Correo requerido")

    # Validación básica de email
    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Formato de correo inválido")

    try:
        # Buscar usuario existente
        usuario = db.query(UserModel).filter(UserModel.email == email).first()

        if not usuario:
            # Crear usuario automáticamente
            username = email.split("@")[0]

            # Verificar que el username no exista
            existing_username = db.query(UserModel).filter(
                UserModel.username == username
            ).first()
            if existing_username:
                import time
                username = f"{username}{int(time.time()) % 10000}"

            usuario = UserModel(
                nombre=nombre,
                username=username,
                email=email,
                password=None,
                role="user",
                estado="A",
                servicio_id=None
            )
            db.add(usuario)
            db.commit()
            db.refresh(usuario)

            # Enviar correo de bienvenida
            import asyncio
            asyncio.create_task(send_welcome_email(email, nombre, username))
        else:
            username = usuario.username

        # Generar JWT
        access_token = create_access_token({"sub": username})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "usuario": {
                "username": username,
                "email": email,
                "nombre": nombre,
                "role": usuario.role,
                "servicio_id": usuario.servicio_id
            }
        }

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error en autenticación: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
