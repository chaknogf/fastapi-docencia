from sqlalchemy import Column, Integer, String, Text, Date, Boolean, CHAR, ForeignKey, DateTime, Float, BigInteger, Time
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, deferred
from datetime import datetime
from app.database.db import Base


# =========================================================
# Modelo de tabla "lugares_de_realizacion"
# =========================================================
class LugaresModel(Base):
    __tablename__ = "lugares_de_realizacion"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    

    # Relación con ActividadesModel
    # actividades = relationship("ActividadesModel", back_populates="actividad")

# =========================================================
# Modelo de tabla "grupo_edad"
# =========================================================
class GrupoEdadModel(Base):
    __tablename__ = "grupo_edad"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True) 
    rango = Column(String(50), nullable=False)
    


# =========================================================
# Modelo de tabla "actividad"
# =========================================================
class Actividad(Base):
    __tablename__ = "actividad"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    activo = Column(Boolean, default=True, nullable=False)

    # Relación con ActividadesModel
    actividades = relationship("ActividadesModel", back_populates="actividad")

# =========================================================
# Modelo de tabla "modalidad"   
# =========================================================
class Modalidad(Base):
    __tablename__ = "modalidad"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(1), nullable=False)
    nombre = Column(String(50), nullable=False)

    # Relación con ActividadesModel
    actividades = relationship("ActividadesModel", back_populates="modalidad")
    
# =========================================================
# Modelo de tabla "estado"
# =========================================================
class Estado(Base):
    __tablename__ = "estado"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(1), nullable=False)
    nombre = Column(String(50), nullable=False)

    actividades = relationship("ActividadesModel", back_populates="estado")
   