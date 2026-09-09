"""
Módulo de logging centralizado para FastAPI Docencia.
Proporciona configuración consistente de logging en toda la aplicación.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# ===========================================
# CONFIGURACIÓN DE LOGGING
# ===========================================

class LoggingConfig:
    """Configuración centralizada de logging."""

    # Formatos
    CONSOLE_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    FILE_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
    JSON_FORMAT = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "function": "%(funcName)s", "line": %(lineno)d, "message": "%(message)s"}'

    # Niveles por defecto
    DEFAULT_LEVEL = logging.INFO
    SQL_LEVEL = logging.WARNING  # Reducir ruido de SQLAlchemy

    # Archivos de log
    LOG_DIR = Path("logs")
    APP_LOG = "app.log"
    ERROR_LOG = "errors.log"
    ACCESS_LOG = "access.log"
    MAX_SIZE_MB = 10
    BACKUP_COUNT = 5

    @classmethod
    def setup_logging(
        cls,
        environment: Optional[str] = None,
        log_level: Optional[int] = None,
        enable_file_logging: bool = True,
        enable_console_logging: bool = True
    ) -> logging.Logger:
        """
        Configura el sistema de logging de la aplicación.

        Args:
            environment: 'development' o 'production'
            log_level: Nivel de logging (logging.DEBUG, INFO, etc.)
            enable_file_logging: Habilitar logging a archivo
            enable_console_logging: Habilitar logging a consola

        Returns:
            Logger raíz configurado
        """
        # Determinar entorno
        if environment is None:
            environment = os.getenv("ENVIRONMENT", "development")

        # Determinar nivel
        if log_level is None:
            log_level = logging.DEBUG if environment == "development" else logging.INFO

        # Crear directorio de logs
        if enable_file_logging:
            cls.LOG_DIR.mkdir(exist_ok=True)

        # Configurar logger raíz
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # Limpiar handlers existentes
        root_logger.handlers.clear()

        # Formatter
        console_formatter = logging.Formatter(cls.CONSOLE_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
        file_formatter = logging.Formatter(cls.FILE_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")

        # Console Handler
        if enable_console_logging:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)

        # File Handler - App Log
        if enable_file_logging:
            app_log_path = cls.LOG_DIR / cls.APP_LOG
            app_handler = logging.handlers.RotatingFileHandler(
                app_log_path,
                maxBytes=cls.MAX_SIZE_MB * 1024 * 1024,
                backupCount=cls.BACKUP_COUNT,
                encoding="utf-8"
            )
            app_handler.setLevel(log_level)
            app_handler.setFormatter(file_formatter)
            root_logger.addHandler(app_handler)

            # File Handler - Error Log
            error_log_path = cls.LOG_DIR / cls.ERROR_LOG
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_path,
                maxBytes=cls.MAX_SIZE_MB * 1024 * 1024,
                backupCount=cls.BACKUP_COUNT,
                encoding="utf-8"
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(file_formatter)
            root_logger.addHandler(error_handler)

        # Configurar loggers de terceros
        cls._configure_third_party_loggers(log_level)

        # Log inicial
        logger = logging.getLogger(__name__)
        logger.info(f"Logging configurado - Entorno: {environment}, Nivel: {logging.getLevelName(log_level)}")

        return root_logger

    @classmethod
    def _configure_third_party_loggers(cls, default_level: int):
        """Configura loggers de librerías de terceros."""
        # SQLAlchemy - reducir ruido
        logging.getLogger("sqlalchemy.engine").setLevel(cls.SQL_LEVEL)
        logging.getLogger("sqlalchemy.pool").setLevel(cls.SQL_LEVEL)
        logging.getLogger("sqlalchemy.dialects").setLevel(cls.SQL_LEVEL)

        # Uvicorn
        logging.getLogger("uvicorn").setLevel(logging.INFO)
        logging.getLogger("uvicorn.access").setLevel(logging.INFO)

        # FastAPI
        logging.getLogger("fastapi").setLevel(logging.INFO)

        # HTTPX
        logging.getLogger("httpx").setLevel(logging.WARNING)

        # APScheduler
        logging.getLogger("apscheduler").setLevel(logging.INFO)


# ===========================================
# HELPER PARA OBTENER LOGGERS
# ===========================================

def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger con el nombre especificado.

    Args:
        name: Nombre del logger (generalmente __name__)

    Returns:
        Logger configurado
    """
    return logging.getLogger(name)


# ===========================================
# MIDDLEWARE DE LOGGING
# ===========================================

class RequestLoggingMiddleware:
    """
    Middleware para loguear requests HTTP.
    """

    def __init__(self, app):
        self.app = app
        self.logger = get_logger("access")

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = datetime.now()

            # Log request
            method = scope.get("method", "UNKNOWN")
            path = scope.get("path", "/")
            self.logger.info(f"Request: {method} {path}")

            # Process request
            await self.app(scope, receive, send)

            # Log response time
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Response: {method} {path} - {duration:.3f}s")
        else:
            await self.app(scope, receive, send)


# ===========================================
# FUNCIÓN PARA CONFIGURAR LOGGING EN MAIN.PY
# ===========================================

def setup_logging(app=None):
    """
    Función principal para configurar logging.
    Llamar al inicio de la aplicación.
    """
    from app.database.config import ENVIRONMENT

    LoggingConfig.setup_logging(
        environment=ENVIRONMENT,
        enable_file_logging=True,
        enable_console_logging=True
    )

    # Agregar middleware de logging si se proporciona app
    if app:
        app.add_middleware(RequestLoggingMiddleware)

    return get_logger(__name__)
