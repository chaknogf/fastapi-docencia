"""
Módulo de Rate Limiting para FastAPI.
Previne abusos y DDoS limitando peticiones por IP.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse


# ===========================================
# CONFIGURACIÓN DEL LIMITER
# ===========================================

# Crear limitador con Redis como store (fallback a memoria)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"],  # Límite por defecto
    storage_uri="memory://",  # Usar Redis en producción: "redis://localhost:6379"
)


# ===========================================
# LÍMITES ESPECÍFICOS POR ENDPOINT
# ===========================================

# Autenticación - Más estricto
AUTH_RATE_LIMIT = "5/minute"

# Escritura (CRUD)
WRITE_RATE_LIMIT = "30/minute"

# Lectura (GET)
READ_RATE_LIMIT = "100/minute"

# Reportes (pueden ser pesados)
REPORT_RATE_LIMIT = "10/minute"

# Endpoints públicos
PUBLIC_RATE_LIMIT = "60/minute"


# ===========================================
# HANDLER DE ERRORES
# ===========================================

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Handler personalizado para cuando se excede el rate limit.
    """
    return JSONResponse(
        status_code=429,
        content={
            "error": "Demasiadas peticiones",
            "detail": f"Límite de {exc.detail} excedido. Intenta de nuevo en un momento.",
            "retry_after": "60 segundos"
        }
    )


# ===========================================
# MIDDLEWARE
# ===========================================

def setup_rate_limiting(app):
    """
    Configura el rate limiting en la aplicación FastAPI.
    """
    # Agregar limiter al app state
    app.state.limiter = limiter

    # Agregar middleware
    app.add_middleware(SlowAPIMiddleware)

    # Agregar handler de errores
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    return app
