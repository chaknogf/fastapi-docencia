# 🚀 GUÍA DE ESCALABILIDAD

## 📐 Estructura Recomendada para Escalar

### 1. Organización por Módulos (Feature-Based)

```
app/
├── modules/
│   ├── users/
│   │   ├── __init__.py
│   │   ├── router.py        # Endpoints
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── service.py       # Lógica de negocio
│   │   ├── repository.py    # Acceso a datos
│   │   └── tests/
│   │       ├── test_router.py
│   │       └── test_service.py
│   │
│   ├── activities/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── service.py
│   │   ├── repository.py
│   │   └── tests/
│   │
│   ├── attendance/
│   │   └── ... (similar estructura)
│   │
│   └── reports/
│       └── ... (similar estructura)
│
├── core/
│   ├── config.py            # Settings centralizadas
│   ├── security.py          # JWT, OAuth2
│   ├── database.py          # Conexión BD
│   └── exceptions.py        # Excepciones personalizadas
│
├── shared/
│   ├── dependencies.py      # Dependencias compartidas
│   ├── pagination.py        # Paginación genérica
│   └── responses.py         # Respuestas estándar
│
└── main.py
```

---

## 🔧 Patrones de Diseño Recomendados

### 1. Repository Pattern

```python
# app/modules/activities/repository.py
from sqlalchemy.orm import Session
from app.modules.activities.models import ActividadesModel

class ActivityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, activity_id: int) -> ActividadesModel | None:
        return self.db.query(ActividadesModel).filter(
            ActividadesModel.id == activity_id
        ).first()

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(ActividadesModel).offset(skip).limit(limit).all()

    def create(self, data: dict) -> ActividadesModel:
        activity = ActividadesModel(**data)
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity

    def update(self, activity_id: int, data: dict) -> ActividadesModel | None:
        activity = self.get_by_id(activity_id)
        if activity:
            for key, value in data.items():
                setattr(activity, key, value)
            self.db.commit()
            self.db.refresh(activity)
        return activity

    def delete(self, activity_id: int) -> bool:
        activity = self.get_by_id(activity_id)
        if activity:
            self.db.delete(activity)
            self.db.commit()
            return True
        return False
```

### 2. Service Layer

```python
# app/modules/activities/service.py
from sqlalchemy.orm import Session
from app.modules.activities.repository import ActivityRepository
from app.modules.activities.schemas import ActividadCreate, ActividadUpdate

class ActivityService:
    def __init__(self, db: Session):
        self.repository = ActivityRepository(db)

    def get_activities(self, skip: int = 0, limit: int = 10):
        return self.repository.get_all(skip=skip, limit=limit)

    def create_activity(self, data: ActividadCreate):
        return self.repository.create(data.model_dump())

    def update_activity(self, activity_id: int, data: ActividadUpdate):
        update_data = data.model_dump(exclude_unset=True)
        return self.repository.update(activity_id, update_data)

    def delete_activity(self, activity_id: int) -> bool:
        return self.repository.delete(activity_id)
```

### 3. Router Limpio

```python
# app/modules/activities/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.activities.service import ActivityService
from app.modules.activities.schemas import (
    ActividadCreate,
    ActividadUpdate,
    ActividadResponse
)

router = APIRouter(prefix="/activities", tags=["activities"])

@router.get("/", response_model=list[ActividadResponse])
def list_activities(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    service = ActivityService(db)
    return service.get_activities(skip=skip, limit=limit)

@router.post("/", response_model=ActividadResponse, status_code=201)
def create_activity(
    data: ActividadCreate,
    db: Session = Depends(get_db)
):
    service = ActivityService(db)
    return service.create_activity(data)

@router.put("/{activity_id}", response_model=ActividadResponse)
def update_activity(
    activity_id: int,
    data: ActividadUpdate,
    db: Session = Depends(get_db)
):
    service = ActivityService(db)
    result = service.update_activity(activity_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Activity not found")
    return result
```

---

## 📊 Estrategias de Caché

### 1. Caché con Redis

```python
# app/core/cache.py
import redis
import json
from functools import wraps
from typing import Callable

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration: int = 300):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator

# Uso
@router.get("/activities/")
@cache_result(expiration=60)
async def list_activities(db: Session = Depends(get_db)):
    # Esta función se cachea por 60 segundos
    ...
```

### 2. Caché de Base de Datos

```python
# Consultas frecuentes que se pueden cachear
# - Catálogos (modalidades, estados, lugares)
# - Listas de usuarios activos
# - Configuraciones del sistema
```

---

## 🔐 Sistema de Permisos

### 1. Decorador de Roles

```python
# app/core/permissions.py
from functools import wraps
from fastapi import HTTPException, status
from app.core.security import get_current_user
from app.modules.users.models import UserModel

def require_role(*roles):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: UserModel = Depends(get_current_user), **kwargs):
            if current_user.role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Uso
@router.delete("/{activity_id}")
@require_role("admin", "coordinator")
async def delete_activity(activity_id: int, ...):
    ...
```

### 2. Permisos por Recurso

```python
# app/core/permissions.py
class Permission:
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"

class ActivityPermission:
    @staticmethod
    def can_create(user: UserModel) -> bool:
        return user.role in ["admin", "coordinator"]

    @staticmethod
    def can_update(user: UserModel, activity) -> bool:
        if user.role == "admin":
            return True
        if user.role == "coordinator":
            return activity.servicio_id == user.servicio_id
        return False
```

---

## 📈 Optimización de Consultas

### 1. Evitar N+1

```python
# ❌ MAL - Consultas N+1
activities = db.query(ActividadesModel).all()
for activity in activities:
    print(activity.servicio.nombre)  # Consulta adicional por cada activity

# ✅ BIEN - Usar joinedload
from sqlalchemy.orm import joinedload

activities = db.query(ActividadesModel).options(
    joinedload(ActividadesModel.servicio),
    joinedload(ActividadesModel.subdireccion)
).all()
```

### 2. Índices en Base de Datos

```sql
-- Índices recomendados
CREATE INDEX idx_actividades_fecha ON actividades(fecha_programada);
CREATE INDEX idx_actividades_estado ON actividades(estado_id);
CREATE INDEX idx_actividades_servicio ON actividades(servicio_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

### 3. Paginación Eficiente

```python
# app/shared/pagination.py
from pydantic import BaseModel
from typing import TypeVar, Generic, List
from sqlalchemy.orm import Query

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    size: int
    pages: int
    items: List[T]

def paginate(query: Query, page: int = 1, size: int = 10) -> dict:
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    pages = (total + size - 1) // size
    return {
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
        "items": items
    }
```

---

## 🧪 Estrategia de Testing

### 1. Tests Unitarios

```python
# tests/unit/test_activity_service.py
import pytest
from unittest.mock import Mock, patch
from app.modules.activities.service import ActivityService

def test_create_activity():
    db = Mock()
    service = ActivityService(db)
    data = {"tema": "Test", "actividad_id": 1}
    result = service.create_activity(data)
    assert result is not None
    db.add.assert_called_once()
```

### 2. Tests de Integración

```python
# tests/integration/test_activity_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_activity():
    response = client.post(
        "/activities/",
        json={"tema": "Test Activity", "actividad_id": 1},
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 201
    assert "id" in response.json()
```

---

## 🐳 Dockerización

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/docencia
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=docencia
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📋 Resumen de Escalabilidad

| Área | Acción | Prioridad |
|------|--------|-----------|
| Arquitectura | Feature-based modules | Alta |
| Patrones | Repository + Service | Alta |
| Caché | Redis para consultas | Media |
| Testing | Unit + Integration | Alta |
| Permisos | Sistema de roles | Media |
| Docker | Containerización | Media |
| CI/CD | GitHub Actions | Baja |
| Monitoring | Sentry/APM | Baja |

---

*Guía de escalabilidad: 2026-09-09*
