from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
    

# schemas.py o models.py



class UserBase(BaseModel):
    nombre: str
    username: str
    email: EmailStr
    password: str
    role: str
    estado: str = "A"
    servicio_id: Optional[int] = None
    # google_id: Optional[str] = None

class UserCreate(UserBase):
    pass  # No incluir 'id'

class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)