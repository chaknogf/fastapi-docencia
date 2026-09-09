"""
FastAPI Docencia - Punto de entrada principal
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.routes.otros_valores import router as otros_valores
from app.routes.user import router as user
from app.routes.actividad import router as actividad
from app.routes.servicios_responsables import router as servicios
from app.routes.subdireccion import router as subdireccion
from app.routes.funciones import router as funciones
from app.routes.asistencia import router as asistencia
from app.routes.reporte import router as reporte
from app.routes.auth import router as auth
from app.database.db import engine, SessionLocal
from app.database.config import ENVIRONMENT
from app.core.rate_limiting import setup_rate_limiting, limiter
from app.core.logging_config import setup_logging, get_logger

# Configurar logging
setup_logging()
logger = get_logger(__name__)


# ===========================================
# SCHEDULER
# ===========================================

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación."""
    logger.info("Iniciando aplicación FastAPI Docencia v3.0.0")

    # Programar tareas
    scheduler.add_job(
        enviar_correos_mensuales_worker,
        CronTrigger(day=1, hour=8, minute=0),
        id="envio_mensual_actividades",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler de tareas iniciado")

    yield

    # Apagar
    scheduler.shutdown(wait=False)
    logger.info("Aplicación detenida correctamente")


def enviar_correos_mensuales_worker():
    """Worker para envío de correos mensuales."""
    worker_logger = get_logger("worker.monthly_emails")
    from app.routes.funciones import enviar_correos_mensuales

    db = SessionLocal()
    try:
        worker_logger.info("Iniciando envío de correos mensuales...")
        enviados = enviar_correos_mensuales(db)
        worker_logger.info(f"Correos mensuales enviados: {enviados}")
    except Exception as e:
        worker_logger.error(f"Error en envío automático mensual: {e}", exc_info=True)
    finally:
        db.close()


# ===========================================
# APLICACIÓN FASTAPI
# ===========================================

app = FastAPI(
    title="FASTAPI DOCENCIA",
    version="3.0.0",
    description="API de gestión de docencia y capacitaciones",
    root_path="/fad",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ===========================================
# MIDDLEWARE
# ===========================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting
setup_rate_limiting(app)


# ===========================================
# ENDPOINTS BÁSICOS
# ===========================================

@app.get("/health", tags=["system"])
@limiter.exempt
def health():
    """Health check de la aplicación."""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return {
            "status": "ok",
            "database": "connected",
            "version": "3.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "database": str(e)
        }


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirige a la documentación."""
    return RedirectResponse(url="/docs")


# ===========================================
# ROUTERS
# ===========================================

app.include_router(auth, prefix="/fad", tags=["auth"])
app.include_router(user, prefix="/fad", tags=["users"])
app.include_router(actividad, prefix="/fad", tags=["actividades"])
app.include_router(servicios, prefix="/fad", tags=["servicios"])
app.include_router(subdireccion, prefix="/fad", tags=["subdirecciones"])
app.include_router(otros_valores, prefix="/fad", tags=["otros"])
app.include_router(funciones, prefix="/fad", tags=["funciones"])
app.include_router(asistencia, prefix="/fad", tags=["asistencia"])
app.include_router(reporte, prefix="/fad", tags=["reportes"])


# ===========================================
# EJECUCIÓN
# ===========================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=ENVIRONMENT == "development"
    )
