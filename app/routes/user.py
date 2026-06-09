from datetime import date, datetime, time, timedelta
from jose import JWTError, jwt
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, desc
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from app.database.db import SessionLocal
from app.database.config import SECRET_KEY, ALGORITHM
from app.database.security import create_access_token, hash_password, verify_password, pwd_context, get_current_user, oauth2_scheme
from app.models.user import UserModel
from sqlalchemy.orm import Session as SQLAlchemySession
from passlib.context import CryptContext
from app.schemas.schemas import TokenResponse, UserCreate, UserBase, UserResponse, UserUpdate, RecuperarContrasenaRequest, RestablecerContrasenaRequest
from app.config.mail_config import conf
import asyncio
from fastapi_mail import FastMail, MessageSchema, MessageType



router = APIRouter() 
#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
@router.get("/user/", response_model=List[UserResponse], tags=["users"])
async def get_users(
    id: Optional[int] = Query(None, description="ID del usuario"),
    nombre: Optional[str] = Query(None, description="Nombre del usuario"),
    username: Optional[str] = Query(None, description="Username del usuario"),
    email: Optional[str] = Query(None, description="Email del usuario"),
    role: Optional[str] = Query(None, description="Role del usuario"),
    current_user: str = Depends(get_current_user),  # Esto ya valida el token
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=0),
    db: SQLAlchemySession = Depends(get_db)
):
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
       return JSONResponse(status_code=200, content=jsonable_encoder(result))

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
        
        
# Ruta para crear un nuevo usuario
@router.post("/user/crear", tags=["users"])
async def create_user(
    user: UserCreate, 
    current_user: str = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db)):
    try:
        # Asegúrate de que la contraseña esté cifrada
        if user.password:
            hashed_password = pwd_context.hash(user.password)
            user.password = hashed_password

        # Crear el nuevo usuario con los datos proporcionados
        new_user = UserModel(**user.model_dump())
        
        # Añadir y confirmar el nuevo usuario en la base de datos
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Retornar el nuevo usuario en formato JSON
        return JSONResponse(status_code=200, content={"message": "User created successfully"})
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put(
    "/user/actualizar/{user_id}",
    tags=["users"],
    response_model=UserResponse
)
async def update_user(
    user_id: int,
    user: UserUpdate,
    current_user: str = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db)
):
    # if not current_user["is_admin"] and current_user["sub"] != str(user_id):
    #     raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        data = user.model_dump(exclude_unset=True)

        campos_permitidos = {"nombre", "username", "email", "estado", "servicio_id", "role"}

        for key, value in data.items():
            if key in campos_permitidos:
                setattr(db_user, key, value)

        db.commit()
        db.refresh(db_user)

        return db_user

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error" + str(e))
    
    
@router.delete("/user/eliminar/{user_id}", tags=["users"])
async def delete_user(
    user_id: int, 
    current_user: str = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db)):
    try:
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(db_user)
        db.commit()
        return JSONResponse(status_code=200, content={"message": "User deleted successfully"})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
# ==============================
# CREAR USUARIO Y ENVIAR CORREO
# ==============================
@router.post("/user/registro", tags=["users"])
async def create_user(user: UserCreate, db: SQLAlchemySession = Depends(get_db)):
    try:
        # 🔐 Guardar la contraseña plana temporalmente para el correo
        contraseña_plana = user.password

        # 📌 Hashear contraseña con Argon2 antes de guardar en DB
        if user.password:
            user.password = pwd_context.hash(user.password)

        # 📦 Crear el usuario en la base de datos
        new_user = UserModel(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # 💌 Enviar correo de bienvenida
        fm = FastMail(conf)
        message = MessageSchema(
            subject="Bienvenido a Docencia Tecpán 🎉",
            recipients=[new_user.email],
            body=f"""
            <h2>¡Hola {new_user.nombre}!</h2>
            <p>Tu cuenta ha sido creada exitosamente en el sistema de docencia.</p>
            <p>Ingresa a: <a href="https://www.hosptecpan.space/cartelera/eventos">Cartelera de eventos</a></p>
            <p><b>Usuario:</b> {new_user.username}</p>
            <p><b>Correo:</b> {new_user.email}</p>
            <p><b>Contraseña:</b> {contraseña_plana}</p>
            <p>¡Bienvenido a bordo!</p>
            """,
            subtype=MessageType.html
        )

        try:
            await fm.send_message(message)
        except Exception as mail_error:
            # 🔴 Log de error para depuración
            print("Error enviando correo:", mail_error)
            raise HTTPException(status_code=500, detail=f"Error enviando correo: {mail_error}")

        return JSONResponse(
            status_code=201,
            content={
                "message": "Usuario creado exitosamente y correo enviado",
                "usuario": {
                    "nombre": new_user.nombre,
                    "email": new_user.email,
                    "username": new_user.username
                }
            }
        )

    except SQLAlchemyError as db_error:
        raise HTTPException(status_code=500, detail=f"Error en base de datos: {db_error}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e}")


# ==============================
# RECUPERAR CONTRASEÑA (SOLICITUD)
# ==============================
@router.post("/user/recuperar-contrasena", tags=["users"])
async def recuperar_contrasena(
    data: RecuperarContrasenaRequest,
    db: SQLAlchemySession = Depends(get_db),
):
    try:
        usuario = db.query(UserModel).filter(UserModel.email == data.email).first()
        if not usuario:
            return {"message": "Si el correo existe, recibirás instrucciones para restablecer tu contraseña"}

        reset_token = create_access_token(
            data={"sub": usuario.username, "purpose": "password_reset"},
            expires_delta=timedelta(minutes=30),
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
            print("Error enviando correo de recuperación:", mail_error)
            raise HTTPException(status_code=500, detail="Error al enviar el correo de recuperación")

        return {"message": "Si el correo existe, recibirás instrucciones para restablecer tu contraseña"}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error en base de datos: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e}")


# ==============================
# RESTABLECER CONTRASEÑA
# ==============================
@router.post("/user/restablecer-contrasena", tags=["users"])
async def restablecer_contrasena(
    data: RestablecerContrasenaRequest,
    db: SQLAlchemySession = Depends(get_db),
):
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")

    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
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
        raise HTTPException(status_code=500, detail=f"Error en base de datos: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e}")


