from sqlalchemy import Column, Integer, String, Text, JSON, CHAR, Float, desc
from sqlalchemy.dialects.postgresql import JSONB
from app.database.db import Base

class ActividadesModel(Base):
    __tablename__ = "actividades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tema = Column(Text, nullable=False)
    actividad = Column(Integer, nullable=False)
    servicio_encargado = Column(Text, nullable=False)
    persona_responsable = Column(JSONB, nullable=True)
    tiempo_aproximado = Column(String(50), nullable=True)
    fechas_a_desarrollar = Column(String(50), nullable=True)
    modalidad = Column(CHAR(2), nullable=False)
    estado = Column(CHAR(2), nullable=False)
    detalles = Column(JSONB, nullable=True)
    metadatos = Column(JSONB, nullable=True)
    
class VistaReporte(Base):
    __tablename__ = "vista_reporte"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    tema = Column(String)
    actividad = Column(String)
    servicio_encargado = Column(String)
    fechas_a_desarrollar = Column(String)
    modalidad = Column(String)
    estado = Column(String)
    mes = Column(Integer)
    anio = Column(Integer)
    fecha_entrega_informe = Column(String)
    nota = Column(String)
    
    
class VistaEjecucion(Base):
    __tablename__ = "vista_ejecucion"

    anio = Column(Integer, primary_key=True, index=True)
    estado = Column(String, primary_key=True, index=True)
    total_estado = Column(Integer)
    porcentaje = Column(Float)


class VistaEjecucionServicio(Base):
    __tablename__ = "vista_servicios"

    anio = Column(Integer, primary_key=True, index=True)
    servicio_encargado = Column(String, primary_key=True, index=True)
    total = Column(Integer)
    completado = Column(Integer)
    reprogramado = Column(Integer)
    anulado = Column(Integer)
    porcentaje = Column(Float)
    nota = Column(String)
    
    
    
