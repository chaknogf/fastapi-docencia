from sqlalchemy import Column, Integer, String, Text, JSON, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from app.database.db import Base


Base = declarative_base()

class VistaReporte(Base):
    __tablename__ = "vista_reporte"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    tema = Column(String)
    actividad = Column(Integer)
    servicio_encargado = Column(String)
    fechas_a_desarrollar = Column(String)
    modalidad = Column(String)
    estado = Column(String)
    mes = Column(String)  # Puedes usar Integer si casteas en la vista
    fecha_entrega_informe = Column(String)