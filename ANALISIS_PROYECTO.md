# 🔍 ANÁLISIS DEL PROYECTO - Deuda Técnica y Mejoras

## 📊 Resumen Ejecutivo

| Aspecto | Estado | Nota |
|---------|--------|------|
| Arquitectura | ⭐⭐⭐ | Buena estructura, mejorable |
| Seguridad | ⭐⭐⭐⭐ | JWT + Argon2, faltan validaciones |
| Testing | ⭐ | No existen tests |
| Documentación | ⭐⭐ | Swagger disponible, falta docs |
| escalabilidad | ⭐⭐⭐ | Modular, requiere optimización |

---

## ⚠️ Problemas Identificados

### 🔴 Críticos

#### 1. **Duplicación de `get_db()`**
```python
# Se repite en MÚLTIPLES archivos:
# - app/routes/actividad.py (línea 42-51)
# - app/routes/user.py (línea 27-32)
# - app/routes/funciones.py (línea 22-27)
# - app/routes/asistencia.py (línea 23-31)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
**Solución**: Usar `app/apicore/deps.py` o `app/database/db.py` como dependencia central.

#### 2. **Relaciones mal definidas en `asistencia.py`**
```python
# Línea 14 y 23 - Las relaciones están FUERA de la clase
asistencias = relationship("Asistencia", back_populates="pertenencias")
```
**Solución**: Mover relaciones dentro de las clases de modelo.

#### 3. **Secret Key hardcodeada**
```python
# app/database/config.py línea 22
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "e87cbfc88ff202c6442638d03d576513d01c153e8e1bdeb2eebc4832088ec9be"
)
```
**Solución**: Requerir variables de entorno obligatorias.

---

### 🟡 Moderados

#### 4. **Falta validación de autenticación**
Varios endpoints críticos no requieren autenticación:
- `POST /fad/actividad/crear/` (línea 136-163)
- `GET /fad/actividades/` (línea 57-131)
- `POST /fad/asistencia/` (línea 37-56)

#### 5. **Manejo inconsistente de errores**
```python
# Ejemplo en actividad.py
except SQLAlchemyError as e:
    raise HTTPException(status_code=500, detail=str(e))  # Expone detalles internos
```

#### 6. **Tipos de retorno inconsistentes**
- Algunos endpoints retornan `JSONResponse`
- Otros retornan diccionarios directamente
- Faltan `response_model` en varios endpoints

---

### 🟢 Menores

#### 7. **Variables de entorno no validadas**
No hay validación al iniciar si faltan variables críticas.

#### 8. **Sin paginación en algunos endpoints**
- `GET /fad/asistencia/` no tiene paginación

#### 9. **Imports no utilizados**
```python
# En multiples archivos
from app.database.db import SessionLocal  # Duplicado
```

---

## 🛠️ Mejoras Propuestas

### Prioridad 1: Corrección de Bugs

```python
# 1. Corregir modelos asistencia.py
class PertenenciaCulturalModel(Base):
    __tablename__ = "pertenencia_cultural"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    # ✅ Relación DENTRO de la clase
    asistencias = relationship("Asistencia", back_populates="pertenencia")

class SexoModel(Base):
    __tablename__ = "sexo"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    # ✅ Relación DENTRO de la clase
    asistencias = relationship("Asistencia", back_populates="sexo")
```

### Prioridad 2: Centralizar Dependencias

```python
# app/database/deps.py (NUEVO)
from app.database.db import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Prioridad 3: Seguridad

```python
# Requerir autenticación en endpoints críticos
@router.post("/actividad/crear/", status_code=201)
async def crear_actividad(
    actividad: ActividadBase,
    current_user: UserModel = Depends(get_current_user),  # ✅ Agregar
    db: SQLAlchemySession = Depends(get_db)
):
    ...
```

---

## 📋 Checklist de Implementación

### Fase 1: Estabilidad (1-2 días)
- [ ] Corregir relaciones en `asistencia.py`
- [ ] Centralizar `get_db()` en un solo archivo
- [ ] Agregar validación de variables de entorno
- [ ] Eliminar imports no utilizados

### Fase 2: Seguridad (2-3 días)
- [ ] Agregar autenticación a endpoints críticos
- [ ] Implementar rate limiting
- [ ] Revisar permisos por rol
- [ ] Audit logging para acciones sensibles

### Fase 3: Calidad (3-5 días)
- [ ] Crear tests unitarios para modelos
- [ ] Crear tests de integración para endpoints
- [ ] Estándarizar respuestas de error
- [ ] Agregar paginación donde falta

### Fase 4: Escalabilidad (5-7 días)
- [ ] Implementar caché con Redis
- [ ] Optimizar queries N+1
- [ ] Agregar índices en BD
- [ ] Implementar búsqueda full-text

---

## 📊 Métricas de Código

| Métrica | Actual | Objetivo |
|---------|--------|----------|
| Cobertura tests | 0% | >70% |
| Duplicación get_db | 4 | 1 |
| Endpoints con auth | ~40% | >80% |
| Documentación | Básica | Completa |

---

## 🎯 Roadmap de Mejoras

### Corto Plazo (1-2 semanas)
1. Corregir bugs críticos
2. Centralizar dependencias
3. Agregar tests básicos

### Mediano Plazo (1 mes)
1. Sistema de permisos completo
2. Caché para consultas frecuentes
3. Logging centralizado

### Largo Plazo (3 meses)
1. Microservicios (si escala)
2. GraphQL (opcional)
3. Monitoreo APM

---

*Análisis generado: 2026-09-09*
