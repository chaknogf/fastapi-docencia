from sqlalchemy import Column, Integer, String, Text, JSON, CHAR
from app.database.db import Base

class ActividadesModel(Base):
    __tablename__ = "actividades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tema = Column(Text, nullable=False)
    actividad = Column(Integer, nullable=False)
    servicio_encargado = Column(Text, nullable=False)
    persona_responsable = Column(JSON, nullable=True)
    tiempo_aproximado = Column(String(50), nullable=True)
    fechas_a_desarrollar = Column(String(50), nullable=True)
    modalidad = Column(CHAR(2), nullable=False)
    estado = Column(CHAR(2), nullable=False)
    detalles = Column(JSON, nullable=True)
    metadatos = Column(JSON, nullable=True)