from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.routes.otros_valores import router as otros_valores
from app.routes.user import router as user
from app.routes.actividad import router as actividad
from app.routes.servicios_responsables import router as servicios
from app.routes.funciones import router as funciones
from app.routes.asistencia import router as asistencia
from app.routes.reporte import router as reporte
from app.auth.login import router as login



app = FastAPI(
    title="FASTAPI DOCENCIA",
    version="3.0.0",
    description="Documentación de la API FastAPI Docencia",
    root_path="/fad"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "https://www.hosptecpan.space"
    ],
    allow_credentials=True,  # ✅ ahora sí es válido
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(login)
app.include_router(user)
app.include_router(actividad)
app.include_router(servicios)
app.include_router(otros_valores)
app.include_router(funciones)
app.include_router(asistencia)
app.include_router(reporte)




@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

