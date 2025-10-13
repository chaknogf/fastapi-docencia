from sqlalchemy import Column, Integer, String, Text, Date, Boolean, CHAR, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, deferred
from datetime import datetime
from app.database.db import Base


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
   


# =========================================================
# Modelo de tabla "subdireccion_perteneciente"
# =========================================================
class Subdireccion_Perteneciente(Base):
    __tablename__ = "subdireccion_perteneciente"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(80), nullable=False)
    descripcion = Column(Text)
    activo = Column(Boolean, default=True, nullable=False)

    # Relación: una subdirección tiene varios servicios
    servicios = relationship("ServicioEncargado", back_populates="subdireccion")
    actividades = relationship("ActividadesModel", back_populates="subdireccion")


# =========================================================
# Modelo de tabla "servicio_encargado"
# =========================================================
class ServicioEncargado(Base):
    __tablename__ = "servicio_encargado"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(Text, nullable=False)
    descripcion = Column(Text)
    activo = Column(Boolean, default=True, nullable=False)

    # 🔑 Llave foránea hacia subdirección
    subdireccion_id = Column(Integer, ForeignKey("subdireccion_perteneciente.id", ondelete="SET NULL", onupdate="CASCADE"))

    # Relaciones inversas
    subdireccion = relationship("Subdireccion_Perteneciente", back_populates="servicios")
    actividades = relationship("ActividadesModel", back_populates="servicio")  

# =========================================================
# Modelo de tabla "meses"
# =========================================================
    
class Mes(Base):
    __tablename__ = "meses"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(20), nullable=False, unique=True)
    actividades = relationship("ActividadesModel", back_populates="mes_obj")  # Relación con nombre coincidente

# =========================================================
# Modelo principal "actividades"
# =========================================================
class ActividadesModel(Base):
    __tablename__ = "actividades"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    tema = Column(Text, nullable=False)
    
    # Llaves foráneas
    actividad_id = Column(Integer, ForeignKey("actividad.id"), nullable=False)
    servicio_id = Column(Integer, ForeignKey("servicio_encargado.id"), nullable=False)
    subdireccion_id = Column(Integer, ForeignKey("subdireccion_perteneciente.id"), nullable=False)
    modalidad_id = Column(Integer, ForeignKey("modalidad.id"), nullable=False)
    estado_id = Column(Integer, ForeignKey("estado.id"), nullable=False)
    mes_id = Column(Integer, ForeignKey("meses.id"), nullable=True)

    # Datos JSON
    persona_responsable = Column(JSONB, nullable=True)
    detalles = Column(JSONB, nullable=True)
    metadatos = Column(JSONB, nullable=True)

    # Campos generales
    tiempo_aproximado = Column(String(50), nullable=True)
    fecha_programada = Column(Date, nullable=True)

    # Relaciones ORM
    actividad = relationship("Actividad", back_populates="actividades")
    servicio = relationship("ServicioEncargado", back_populates="actividades")
    subdireccion = relationship("Subdireccion_Perteneciente", back_populates="actividades")
    modalidad = relationship("Modalidad", back_populates="actividades")
    estado = relationship("Estado", back_populates="actividades")
    mes_obj = relationship("Mes", back_populates="actividades")  # <--- CORRECCIÓN

# =========================================================
# Vista de actividades completa
# =========================================================
class VistaActividad(Base):
    __tablename__ = "vista_actividades_completa"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    tema = Column(Text)
    actividad = Column(String)
    actividad_id = Column(Integer)
    descripcion_actividad = Column(Text)
    subdireccion = Column(String)
    subdireccion_id = Column(Integer)
    servicio_encargado = Column(String)
    servicio_id = Column(Integer)
    persona_responsable = Column(JSONB)
    tiempo_aproximado = Column(String)
    fecha_programada = Column(Date)
    mes = Column(String)
    mes_id = Column(Integer)
    anio = Column(Integer)
    modalidad = Column(String)
    modalidad_id = Column(Integer)
    estado = Column(String)
    estado_id = Column(Integer)
    detalles = Column(JSONB)
    metadatos = Column(JSONB)

# =========================================================
# Vista de reporte resumido
# =========================================================
class VistaReporte(Base):
    __tablename__ = "vista_reporte"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    tema = Column(String)
    actividad = Column(String)
    servicio_encargado = Column(String)
    fecha_programada = Column(Date)
    mes = Column(String)
    mes_id = Column(Integer)
    anio = Column(Integer)
    modalidad = Column(String)
    estado = Column(String)
    nota = Column(String)

# =========================================================
# Vista ejecución por estado
# =========================================================
class VistaEjecucion(Base):
    __tablename__ = "vista_ejecucion"
    __table_args__ = {'extend_existing': True}

    mes_id = Column(Integer, primary_key=True, index=True)
    mes = Column(String)
    anio = Column(Integer, primary_key=True, index=True)
    estado_id = Column(Integer)
    estado = Column(String)
    servicio_id = Column(Integer)
    servicio_encargado = Column(String)
    subdireccion_id = Column(Integer)
    subdireccion = Column(String)
    total_actividades = Column(Integer)
