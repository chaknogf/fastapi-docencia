from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.routes.user import router as user
from app.routes.actividad import router as actividad
from app.auth.login import router as login



app = FastAPI(
    title="FASTAPI DOCENCIA",
    version="3.0.0",
    description="Documentación de la API FastAPI Docencia",
    root_path="/fad"
)

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




@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

