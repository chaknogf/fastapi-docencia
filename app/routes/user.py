from datetime import timedelta
import logging

from jose import JWTError, jwt
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import desc
from typing import List, Optional

from app.database.db import get_db
from app.database.config import SECRET_KEY, ALGORITHM
from app.database.security import (
    create_access_token,
    hash_password,
    verify_password,
    pwd_context,
    get_current_user,
    get_current_admin_user,
)
from app.models.user import UserModel
from sqlalchemy.orm import Session as SQLAlchemySession
from app.schemas.schemas import (
    TokenResponse,
    UserCreate,
    UserBase,
    UserResponse,
    UserUpdate,
    RecuperarContrasenaRequest,
    RestablecerContrasenaRequest,
)
from app.config.mail_config import conf
from app.core.rate_limiting import limiter, AUTH_RATE_LIMIT, WRITE_RATE_LIMIT
from fastapi_mail import FastMail, MessageSchema, MessageType

logger = logging.getLogger(__name__)

router = APIRouter()


# =========================
# ENDPOINT: LISTAR USUARIOS
# =========================
@router.get("/user/", response_model=List[UserResponse], tags=["users"])
async def get_users(
    id: Optional[int] = Query(None, description="ID del usuario"),
    nombre: Optional[str] = Query(None, description="Nombre del usuario"),
    username: Optional[str] = Query(None, description="Username del usuario"),
    email: Optional[str] = Query(None, description="Email del usuario"),
    role: Optional[str] = Query(None, description="Role del usuario"),
    current_user: UserModel = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=0, le=100),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Lista usuarios con filtros y paginación.
    """
    try:
        query = db.query(UserModel).order_by(desc(UserModel.id))

        if id:
            query = query.filter(UserModel.id == id)
        if nombre:
            query = query.filter(UserModel.nombre.ilike(f"%{nombre}%"))
        if username:
            query = query.filter(UserModel.username.ilike(f"%{username}%"))
        if email:
            query = query.filter(UserModel.email.ilike(f"%{email}%"))
        if role:
            query = query.filter(UserModel.role == role)

        result = query.offset(skip).limit(limit).all()
        return result

    except SQLAlchemyError as e:
        logger.error(f"Error al listar usuarios: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener usuarios")


# =========================
# ENDPOINT: CREAR USUARIO (ADMIN)
# =========================
@router.post(
    "/user/crear",
    tags=["users"],
    dependencies=[Depends(get_current_admin_user)]
)
async def create_user_admin(
    user: UserCreate,
    current_user: UserModel = Depends(get_current_admin_user),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Crea un usuario (solo administradores).
    """
    try:
        # Verificar si el username ya existe
        existing_user = db.query(UserModel).filter(
            (UserModel.username == user.username) | (UserModel.email == user.email)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="El username o email ya está registrado"
            )

        if user.password:
            user.password = pwd_context.hash(user.password)

        new_user = UserModel(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"message": "Usuario creado exitosamente"}

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear usuario: {e}")
        raise HTTPException(status_code=500, detail="Error al crear usuario")


# =========================
# ENDPOINT: ACTUALIZAR USUARIO
# =========================
@router.put(
    "/user/actualizar/{user_id}",
    tags=["users"],
    response_model=UserResponse
)
async def update_user(
    user_id: int,
    user: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Actualiza un usuario. Admin puede actualizar cualquiera.
    Usuario normal solo puede actualizar su propio perfil (sin role ni estado).
    """
    try:
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Verificar permisos
        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(
                status_code=403,
                detail="No tiene permiso para actualizar este usuario"
            )

        data = user.model_dump(exclude_unset=True)

        # Campos que solo admin puede cambiar
        admin_only_fields = {"role", "estado", "servicio_id"}
        if current_user.role != "admin":
            for field in admin_only_fields:
                if field in data:
                    del data[field]

        for key, value in data.items():
            setattr(db_user, key, value)

        db.commit()
        db.refresh(db_user)

        return db_user

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar usuario: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar usuario")


# =========================
# ENDPOINT: ELIMINAR USUARIO
# =========================
@router.delete(
    "/user/eliminar/{user_id}",
    tags=["users"],
    dependencies=[Depends(get_current_admin_user)]
)
async def delete_user(
    user_id: int,
    current_user: UserModel = Depends(get_current_admin_user),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Elimina un usuario (solo administradores).
    No permite eliminarse a sí mismo.
    """
    try:
        if current_user.id == user_id:
            raise HTTPException(
                status_code=400,
                detail="No puede eliminarse a sí mismo"
            )

        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        db.delete(db_user)
        db.commit()
        return {"message": "Usuario eliminado exitosamente"}

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar usuario: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar usuario")


# =========================
# REGISTRO PUBLICO CON CORREO
# =========================
@router.post("/user/registro", tags=["users"])
async def register_user(user: UserCreate, db: SQLAlchemySession = Depends(get_db)):
    """
    Registra un usuario y envía correo de bienvenida.
    """
    try:
        # Verificar si el username o email ya existen
        existing = db.query(UserModel).filter(
            (UserModel.username == user.username) | (UserModel.email == user.email)
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="El username o email ya está registrado"
            )

        # Guardar contraseña plana temporalmente para el correo
        contrasena_plana = user.password

        # Hashear contraseña
        user.password = pwd_context.hash(user.password)

        # Crear usuario
        new_user = UserModel(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Enviar correo de bienvenida
        fm = FastMail(conf)
        message = MessageSchema(
            subject="Bienvenido a Docencia Tecpán",
            recipients=[new_user.email],
            body=f"""
            <h2>¡Hola {new_user.nombre}!</h2>
            <p>Tu cuenta ha sido creada exitosamente en el sistema de docencia.</p>
            <p>Ingresa a: <a href="https://www.hosptecpan.space/cartelera/eventos">Cartelera de eventos</a></p>
            <p><b>Usuario:</b> {new_user.username}</p>
            <p><b>Correo:</b> {new_user.email}</p>
            <p><b>Contraseña:</b> {contrasena_plana}</p>
            <p>¡Bienvenido a bordo!</p>
            """,
            subtype=MessageType.html
        )

        try:
            await fm.send_message(message)
        except Exception as mail_error:
            logger.error(f"Error enviando correo: {mail_error}")
            # No falla el registro si el correo falla

        return JSONResponse(
            status_code=201,
            content={
                "message": "Usuario creado exitosamente",
                "usuario": {
                    "nombre": new_user.nombre,
                    "email": new_user.email,
                    "username": new_user.username
                }
            }
        )

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error en registro: {e}")
        raise HTTPException(status_code=500, detail="Error al registrar usuario")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en registro: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# =========================
# RECUPERAR CONTRASEÑA
# =========================
@router.post("/user/recuperar-contrasena", tags=["users"])
@limiter.limit(AUTH_RATE_LIMIT)
async def recuperar_contrasena(
    request: Request,
    data: RecuperarContrasenaRequest,
    db: SQLAlchemySession = Depends(get_db),
):
    """
    Solicita recuperación de contraseña. Envía correo con token.
    """
    try:
        usuario = db.query(UserModel).filter(UserModel.email == data.email).first()
        if not usuario:
            # No revelar si el email existe
            return {"message": "Si el correo existe, recibirás instrucciones para restablecer tu contraseña"}

        reset_token = create_access_token(
            data={"sub": usuario.username},
            expires_delta=timedelta(minutes=30),
            purpose="password_reset"
        )

        reset_link = f"https://www.hosptecpan.space/cartelera/restablecer?token={reset_token}"

        fm = FastMail(conf)
        message = MessageSchema(
            subject="Recuperación de contraseña - Docencia Tecpán",
            recipients=[usuario.email],
            body=f"""
            <div style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #2c3e50;">Recuperación de contraseña</h2>
                <p>Hola <strong>{usuario.nombre}</strong>,</p>
                <p>Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace para continuar:</p>
                <p style="text-align: center;">
                    <a href="{reset_link}"
                       style="background-color: #2980b9; color: white; padding: 12px 24px;
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Restablecer contraseña
                    </a>
                </p>
                <p>Este enlace expira en 30 minutos.</p>
                <p>Si no solicitaste este cambio, ignora este mensaje.</p>
                <p>Atentamente,<br><strong>Coordinación de Docencia</strong></p>
            </div>
            """,
            subtype=MessageType.html,
        )

        try:
            await fm.send_message(message)
        except Exception as mail_error:
            logger.error(f"Error enviando correo de recuperación: {mail_error}")

        return {"message": "Si el correo existe, recibirás instrucciones para restablecer tu contraseña"}

    except SQLAlchemyError as e:
        logger.error(f"Error en recuperación: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# =========================
# RESTABLECER CONTRASEÑA
# =========================
@router.post("/user/restablecer-contrasena", tags=["users"])
@limiter.limit(AUTH_RATE_LIMIT)
async def restablecer_contrasena(
    request: Request,
    data: RestablecerContrasenaRequest,
    db: SQLAlchemySession = Depends(get_db),
):
    """
    Restablece la contraseña usando el token de recuperación.
    """
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")

    # Validación de seguridad de contraseña
    if len(data.new_password) < 8:
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 8 caracteres"
        )

    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verificar que el token sea para restablecer contraseña
        if payload.get("purpose") != "password_reset":
            raise HTTPException(status_code=400, detail="Token inválido")

        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=400, detail="Token inválido")

    except JWTError:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")

    try:
        usuario = db.query(UserModel).filter(UserModel.username == username).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        usuario.password = pwd_context.hash(data.new_password)
        db.commit()

        return {"message": "Contraseña restablecida exitosamente"}

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al restablecer contraseña: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
