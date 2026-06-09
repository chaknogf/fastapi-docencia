from typing import Any, Dict, Generic, List, Optional, Sequence, Tuple, Type, TypeVar, Union

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import desc as sa_desc
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.sql import ColumnElement

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: SQLAlchemySession, *, id: int) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_or_404(self, db: SQLAlchemySession, *, id: int) -> ModelType:
        obj = self.get(db, id=id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} no encontrado",
            )
        return obj

    def get_multi(
        self,
        db: SQLAlchemySession,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        descending: bool = True,
        **filters,
    ) -> Sequence[ModelType]:
        query = db.query(self.model)
        for field, value in filters.items():
            if value is not None and hasattr(self.model, field):
                col: ColumnElement = getattr(self.model, field)
                query = query.filter(col == value)
        if order_by and hasattr(self.model, order_by):
            col = getattr(self.model, order_by)
            query = query.order_by(sa_desc(col) if descending else col)
        else:
            query = query.order_by(sa_desc(self.model.id))
        return query.offset(skip).limit(limit).all()

    def create(self, db: SQLAlchemySession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: SQLAlchemySession,
        *,
        id: int,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        db_obj = self.get_or_404(db, id=id)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: SQLAlchemySession, *, id: int) -> ModelType:
        db_obj = self.get_or_404(db, id=id)
        db.delete(db_obj)
        db.commit()
        return db_obj
