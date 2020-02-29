from typing import Union

from sqlalchemy.sql import Selectable
from sqlalchemy.orm import Query
from sqlalchemy.orm.query import _MapperEntity, _ColumnEntity


class SQLAlchemyFacetsError(Exception):
    pass


def get_column(base: Union[Selectable, Query], name: str):
    if isinstance(base, Selectable):
        return getattr(base.c, name).label(name)
    if isinstance(base, Query):
        for entity in base._entities:
            if isinstance(entity, _MapperEntity):
                for e in entity.entities:
                    if hasattr(e, name):
                        return getattr(e, name)
            if isinstance(entity, _ColumnEntity) and entity.column.name == name:
                return entity.column
    raise SQLAlchemyFacetsError(f"No field '{name}' on '{base}'")


def get_primary_key(base: Selectable) -> str:
    for column in base.columns:
        if column.primary_key:
            return column.name
    raise SQLAlchemyFacetsError(f"Could not find any primary key on '{base}'")
