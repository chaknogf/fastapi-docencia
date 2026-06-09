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
from app.auth.login import router as login
from app.database.db import engine, SessionLocal
from app.routes.funciones import enviar_correos_mensuales
from sqlalchemy import text


scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        enviar_correos_mensuales_worker,
        CronTrigger(day=1, hour=8, minute=0),
        id="envio_mensual_actividades",
        replace_existing=True,
    )
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


def enviar_correos_mensuales_worker():
    db = SessionLocal()
    try:
        enviar_correos_mensuales(db)
    except Exception as e:
        print(f"Error en envío automático mensual: {e}")
    finally:
        db.close()


app = FastAPI(
    title="FASTAPI DOCENCIA",
    version="3.0.0",
    description="Documentación de la API FastAPI Docencia",
    root_path="/fad",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": str(e)
        }


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(login)
app.include_router(user)
app.include_router(actividad)
app.include_router(servicios)
app.include_router(subdireccion)
app.include_router(otros_valores)
app.include_router(funciones)
app.include_router(asistencia)
app.include_router(reporte)


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")
