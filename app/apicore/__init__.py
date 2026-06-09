from app.apicore.base_crud import CRUDBase
from app.apicore.base_schema import BaseSchema, PaginatedResponse
from app.apicore.deps import get_db

__all__ = [
    "CRUDBase",
    "BaseSchema",
    "PaginatedResponse",
    "get_db",
]
