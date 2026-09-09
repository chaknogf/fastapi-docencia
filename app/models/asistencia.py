from sqlalchemy import BigInteger, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, validates
from app.database.db import Base
from datetime import datetime, timezone


class PertenenciaCulturalModel(Base):
    __tablename__ = "pertenencia_cultural"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)

    asistencias = relationship("Asistencia", back_populates="pertenencia")


class SexoModel(Base):
    __tablename__ = "sexo"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)

    asistencias = relationship("Asistencia", back_populates="sexo")


class Asistencia(Base):
    __tablename__ = "asistencia"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(150), nullable=False)
    sexo_id = Column(Integer, ForeignKey("sexo.id", ondelete="SET NULL"))
    grupo_edad_id = Column(Integer, ForeignKey("grupo_edad.id", ondelete="SET NULL"))
    cui = Column(BigInteger)
    puesto_funcional = Column(String(100))
    pertenencia_cultural_id = Column(Integer, ForeignKey("pertenencia_cultural.id", ondelete="SET NULL"))
    telefono_email = Column(String(150))
    datos_extras = Column(JSONB, nullable=True)
    capacitacion_id = Column(Integer, ForeignKey("actividades.id", ondelete="CASCADE"), nullable=False)
    fecha_registro = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    pertenencia = relationship("PertenenciaCulturalModel", back_populates="asistencias")
    sexo = relationship("SexoModel", back_populates="asistencias")
    capacitacion = relationship("ActividadesModel", back_populates="asistencias")

    @validates("nombre_completo")
    def convert_nombre(self, key, value):
        return value.upper() if value else value
