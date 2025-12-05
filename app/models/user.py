from sqlalchemy import CHAR, Column, Integer, String, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import Base
from app.models.actividades import Servicio_Encargado_Model

class UserModel(Base):
   __tablename__ = "users"

   id = Column(Integer, primary_key=True, index=True, autoincrement=True)
   nombre = Column(String(100), nullable=False)
   username = Column(String(50), unique=True, nullable=False)
   email = Column(String(100), unique=True, nullable=False)
   password = Column(String(255), nullable=True)
   role = Column(String(50), nullable=False)
   estado = Column(CHAR(1), default='A')
   servicio_id = Column(Integer, ForeignKey(Servicio_Encargado_Model.id), onupdate="CASCADE", nullable=True)
   # google_id = Column(String(100), unique=True, nullable=True)
   servicio = relationship("Servicio_Encargado_Model", back_populates="usuarios")