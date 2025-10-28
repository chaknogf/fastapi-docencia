# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from app.models.user import UserModel
from app.database.security import create_access_token
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import asyncio

router = APIRouter()

# Configuración del correo
conf = ConnectionConfig(
    MAIL_USERNAME="soporte@tuservidor.com",
    MAIL_PASSWORD="TU_CONTRASEÑA",
    MAIL_FROM="ticshosptecpan@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True
)

# Dependencia de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para enviar correo de bienvenida
async def send_welcome_email(email: str, nombre: str, username: str):
    message = MessageSchema(
        subject="Bienvenido a Docencia",
        recipients=[email],
        body=f"Hola {nombre}, tu cuenta ha sido creada con éxito.\n\nTu usuario es: {username}\nAccede con tu correo para iniciar sesión.",
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)

# Endpoint de login/registro por email
@router.post("/auth/email")
async def auth_email(payload: dict, db: Session = Depends(get_db)):
    email = payload.get("email")
    nombre = payload.get("nombre", email.split("@")[0])

    if not email:
        raise HTTPException(status_code=400, detail="Correo requerido")

    # Buscar usuario existente
    usuario = db.query(UserModel).filter(UserModel.email == email).first()

    if not usuario:
        # Crear usuario automáticamente
        username = email.split("@")[0]
        usuario = UserModel(
            nombre=nombre,
            username=username,
            email=email,
            password=None,
            role="usuario",
            estado="A",
            servicio_id=None
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

        # Enviar correo de bienvenida en background
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