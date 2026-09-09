# 🗺️ MAPA DEL PROYECTO - FastAPI Docencia v3.0.0

## 📋 Descripción General
Sistema de gestión de actividades de docencia y capacitaciones. Administra usuarios, actividades, subdirecciones, servicios, reportes y asistencia.

---

## 🏗️ Arquitectura del Proyecto

```
fastapi-docencia/
├── 📁 app/                    # Aplicación principal
│   ├── 📁 apicore/            # Componentes base reutilizables
│   │   ├── base_crud.py       # Operaciones CRUD genéricas
│   │   ├── base_schema.py     # Schemas base Pydantic
│   │   └── deps.py            # Dependencias compartidas
│   ├── 📁 auth/               # Autenticación
│   │   └── login.py           # Endpoints de login
│   ├── 📁 config/             # Configuraciones
│   │   └── mail_config.py     # Configuración de correo
│   ├── 📁 database/           # Conexión y seguridad BD
│   │   ├── config.py          # Variables de entorno JWT
│   │   ├── db.py              # Engine, SessionLocal, Base
│   │   └── security.py        # JWT, hashing, OAuth2
│   ├── 📁 models/             # Modelos SQLAlchemy
│   │   ├── actividades.py     # Modelos de actividades
│   │   ├── asistencia.py      # Modelos de asistencia
│   │   └── user.py            # Modelo de usuario
│   ├── 📁 routes/             # Endpoints API
│   │   ├── actividad.py       # CRUD actividades
│   │   ├── asistencia.py      # CRUD asistencia
│   │   ├── auth.py            # Autenticación
│   │   ├── funciones.py       # Funciones utilitarias
│   │   ├── otros_valores.py   # Catálogos (modalidad, estado, etc.)
│   │   ├── reporte.py         # Generación Excel
│   │   ├── servicios_responsables.py  # Servicios
│   │   ├── subdireccion.py    # Subdirecciones
│   │   └── user.py            # CRUD usuarios
│   └── 📁 schemas/            # Esquemas Pydantic
│       ├── actividad.py       # Schemas actividades
│       ├── asistencia.py      # Schemas asistencia
│       ├── otras.py           # Schemas misceláneos
│       └── schemas.py         # Schemas usuarios
├── 📁 scripts/                # Scripts utilitarios
│   └── setup.sh               # Configuración inicial
├── 📁 sql/                    # Archivos SQL
│   ├── init.sql               # Script inicial de BD
│   └── actividad.sql          # Tablas de actividades
├── 📁 utils/                  # Utilidades
│   └── conversion.py          # Funciones de conversión
├── main.py                    # Punto de entrada FastAPI
├── pyproject.toml             # Dependencias Poetry
└── requirements.txt           # Dependencias pip
```

---

## 🔄 Flujo de la Aplicación

```
                    ┌─────────────────────┐
                    │      main.py        │
                    │   FastAPI App       │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   Routers     │    │  Middleware   │    │   Scheduler   │
│  (endpoints)  │    │    (CORS)    │    │  (APScheduler)│
└───────┬───────┘    └───────────────┘    └───────────────┘
        │
        ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Schemas      │    │    Models     │    │   Database    │
│  (Pydantic)   │◄──►│ (SQLAlchemy)  │◄──►│  (PostgreSQL) │
└───────────────┘    └───────────────┘    └───────────────┘
```

---

## 📊 Modelos de Base de Datos

### 🗂️ Estructura de Tablas

```
┌─────────────────────────────────────────────────────────────────┐
│                        MODELOS PRINCIPALES                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │    users     │     │ actividades  │     │  asistencia  │    │
│  ├──────────────┤     ├──────────────┤     ├──────────────┤    │
│  │ id (PK)      │     │ id (PK)      │     │ id (PK)      │    │
│  │ nombre       │     │ tema         │     │ nombre_completo│   │
│  │ username     │     │ actividad_id │     │ sexo_id (FK) │    │
│  │ email        │     │ servicio_id  │     │ grupo_edad_id│    │
│  │ password     │     │ subdireccion_id│   │ cui          │    │
│  │ role         │     │ modalidad_id │     │ pertenencia_cultural_id│
│  │ estado       │     │ estado_id    │     │ capacitacion_id (FK)│
│  │ servicio_id  │     │ mes_id       │     │ fecha_registro│   │
│  └──────────────┘     │ persona_responsable│ └──────────────┘    │
│                       │ detalles      │                          │
│                       │ metadatos     │                          │
│                       │ fecha_programada│                         │
│                       │ horario_programado│                       │
│                       │ lugar_id      │                          │
│                       └──────────────┘                          │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                        CATÁLOGOS                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  actividad   │  │  modalidad   │  │    estado    │         │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤         │
│  │ id (PK)      │  │ id (PK)      │  │ id (PK)      │         │
│  │ nombre       │  │ codigo       │  │ codigo       │         │
│  │ descripcion  │  │ nombre       │  │ nombre       │         │
│  │ activo       │  └──────────────┘  └──────────────┘         │
│  └──────────────┘                                              │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │    meses     │  │    lugares   │  │  grupo_edad  │         │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤         │
│  │ id (PK)      │  │ id (PK)      │  │ id (PK)      │         │
│  │ nombre       │  │ nombre       │  │ rango        │         │
│  └──────────────┘  │ descripcion  │  └──────────────┘         │
│                    └──────────────┘                             │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                    ORGANIZACIÓN                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐         ┌──────────────┐                     │
│  │subdireccion_ │  1   N  │  servicio_   │                     │
│  │perteneciente │◄───────►│  encargado   │                     │
│  ├──────────────┤         ├──────────────┤                     │
│  │ id (PK)      │         │ id (PK)      │                     │
│  │ nombre       │         │ nombre       │                     │
│  │ descripcion  │         │ descripcion  │                     │
│  │ persona_encargada│     │ encargado_servicio│                │
│  │ activo       │         │ subdireccion_id (FK)│              │
│  └──────────────┘         │ activo       │                     │
│                           └──────────────┘                     │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                          VISTAS                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────┐                               │
│  │  vista_actividades_completa │                               │
│  ├─────────────────────────────┤                               │
│  │ Join de actividades con:    │                               │
│  │ - actividad                 │                               │
│  │ - servicio_encargado        │                               │
│  │ - subdireccion_perteneciente│                               │
│  │ - modalidad                 │                               │
│  │ - estado                    │                               │
│  │ - meses                     │                               │
│  └─────────────────────────────┘                               │
│                                                                  │
│  ┌─────────────────────────────┐                               │
│  │     vista_reporte           │                               │
│  ├─────────────────────────────┤                               │
│  │ Resumen para reportes       │                               │
│  └─────────────────────────────┘                               │
│                                                                  │
│  ┌─────────────────────────────┐                               │
│  │     vista_ejecucion         │                               │
│  ├─────────────────────────────┤                               │
│  │ Ejecución por estado        │                               │
│  └─────────────────────────────┘                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🌐 Endpoints API

### 🔐 Autenticación
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | `/fad/auth/login` | Login usuario | No |
| POST | `/fad/user/registro` | Registro con email | No |
| POST | `/fad/user/recuperar-contrasena` | Solicitud reset | No |
| POST | `/fad/user/restablecer-contrasena` | Reset contraseña | No |

### 👥 Usuarios
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/fad/user/` | Listar usuarios | ✅ |
| POST | `/fad/user/crear` | Crear usuario | ✅ |
| PUT | `/fad/user/actualizar/{id}` | Actualizar usuario | ✅ |
| DELETE | `/fad/user/eliminar/{id}` | Eliminar usuario | ✅ |

### 📚 Actividades
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/fad/actividades/` | Listar actividades | No |
| POST | `/fad/actividad/crear/` | Crear actividad | No |
| PUT | `/fad/actividad/actualizar/{id}` | Actualizar actividad | ✅ |
| DELETE | `/fad/actividad/eliminar/{id}` | Eliminar actividad | ✅ |

### 📋 Asistencia
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/fad/asistencia/` | Listar asistencias | No |
| GET | `/fad/asistencia/{id}` | Obtener asistencia | No |
| POST | `/fad/asistencia/` | Registrar asistencia | No |
| PUT | `/fad/asistencia/{id}` | Actualizar asistencia | No |
| DELETE | `/fad/asistencia/{id}` | Eliminar asistencia | No |

### 📊 Reportes
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/fad/reporte/vista` | Reporte resumido | No |
| GET | `/fad/reporte/ejecucion` | Ejecución por estado | No |
| GET | `/fad/reporte/resumen-anual` | Resumen anual | No |
| GET | `/fad/reporte/excel` | Descargar Excel | No |

### 🔧 Funciones
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | `/fad/actividades/enviar-mensual` | Enviar correos | No |
| POST | `/fad/verificador/` | Validar horarios | No |
| GET | `/fad/health` | Health check | No |

---

## 🔐 Seguridad

### JWT Configuration
- **Algoritmo**: HS256
- **Tiempo expiración**: 24 horas (configurable)
- **Bearer Token**: OAuth2PasswordBearer

### Roles de Usuario
- `admin` - Acceso completo
- `user` - Acceso estándar

### Estados de Usuario
- `A` - Activo
- `I` - Inactivo
- `B` - Bloqueado

---

## 🛠️ Tecnologías

| Categoría | Tecnología | Versión |
|-----------|------------|---------|
| Framework | FastAPI | 0.122.0 |
| ORM | SQLAlchemy | 2.0.44 |
| Base de Datos | PostgreSQL | - |
| Autenticación | python-jose | 3.5.0 |
| Hashing | Argon2 | 25.1.0 |
| Correo | fastapi-mail | 1.5.8 |
| Scheduler | APScheduler | - |
| Reportes | openpyxl | 3.1.5 |
| Validation | Pydantic | 2.12.5 |

---

## 📁 Archivos Clave

### Configuración
| Archivo | Propósito |
|---------|-----------|
| `main.py` | Punto de entrada, configuración FastAPI |
| `pyproject.toml` | Dependencias del proyecto |
| `.env` | Variables de entorno (no versionado) |

### Base de Datos
| Archivo | Propósito |
|---------|-----------|
| `app/database/db.py` | Conexión PostgreSQL |
| `app/database/config.py` | Config JWT y Mail |
| `app/database/security.py` | Autenticación |

### Modelos
| Archivo | Propósito |
|---------|-----------|
| `app/models/user.py` | Modelo usuarios |
| `app/models/actividades.py` | Modelo actividades |
| `app/models/asistencia.py` | Modelo asistencia |

---

## 🚀 Funcionalidades Principales

1. **Gestión de Usuarios**
   - Registro con envío de correo
   - Login con JWT
   - Recuperación de contraseña
   - Roles y permisos

2. **Gestión de Actividades**
   - CRUD completo
   - Filtros avanzados
   - Paginación
   - Estados y modalidades

3. **Reportes**
   - Generación Excel con formato
   - Reporte de ejecución por estado
   - Resumen anual

4. **Automatización**
   - Envío mensual de correos
   - Scheduler para tareas programadas

---

## 🔧 Para Desarrolladores

### Ejecutar en Desarrollo
```bash
# Instalar dependencias
poetry install

# Activar entorno
poetry shell

# Ejecutar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Variables de Entorno (.env)
```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=secreto123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=docencia
SECRET_KEY=tu_clave_secreta
MAIL_USERNAME=tu_email
MAIL_PASSWORD=tu_password
```

---

## 📈 Escalabilidad

### Áreas de Mejora Sugeridas
1. **Testing** - Agregar tests unitarios y de integración
2. **Validación** - Reforzar validación en endpoints
3. **Caching** - Implementar Redis para consultas frecuentes
4. **Logging** - Sistema centralizado de logs
5. **Docker** - Containerización para despliegue
6. **CI/CD** - Pipeline de integración continua

---

*Última actualización: 2026-09-09*
