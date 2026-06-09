from fastapi import Depends
from sqlalchemy.orm import Session as SQLAlchemySession

from app.database.db import get_db as _get_db

get_db = _get_db
