"""Hello SQLAlchemy Facets
I'm a documentation
"""
from typing import Dict, List, Tuple, Type, Any, Sequence, NamedTuple, Union
from collections import OrderedDict

from sqlalchemy import func, distinct, and_
from sqlalchemy.sql import Selectable
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.sql.elements import Label
from sqlalchemy.orm import Query
from sqlalchemy.orm.query import _MapperEntity, _ColumnEntity


class SQLAlchemyFacetsError(Exception):
    pass


class Mapper:

    @staticmethod
    def transform(value: Any) -> str:
        return value

    @staticmethod
    def revert(value: str) -> Any:
        return value


class Facet:
    """I'm the Facet class
    """
    name: str

    def __init__(self, name: str = None, mapper: Mapper = Mapper()):
        self.name = name or self.name
        self.mapper = mapper

    def _labeled_column(self, base: Selectable) -> Label:
        return labeled_column_from_name_on_base(base, self.name)

    def facet_column(self, base: Selectable) -> Label:
        return self._labeled_column(base)

    def filter(self, query: Query, values: List) -> BinaryExpression:
        return labeled_column_from_name_on_query(query, self.name)\
            .in_([self.mapper.revert(v) for v in values])


class ValueCount(NamedTuple):
    value: str
    count: int


class FacetResult:

    def __init__(self, facet: Facet, values_count: List[ValueCount]):
        self.facet = facet
        self.values_count = values_count

    @classmethod
    def from_dual_sequences(cls,
                            facet: Facet,
                            values: Sequence,
                            counts: Sequence) -> "FacetResult":
        return cls(
            facet=facet,
            values_count=sorted([
                ValueCount(
                    value=facet.mapper.transform(v),
                    count=counts[i]
                ) for i, v in enumerate(values) if v is not None],
                key=lambda v: v.count, reverse=True
            )
        )

    def asdict(self) -> Dict[str, Any]:
        return dict(
            name=self.facet.name,
            values=[v._asdict() for v in self.values_count]
        )


class Config(OrderedDict):

    def __init__(self, facets: Sequence[Facet]):
        super().__init__([(f.name, f) for f in facets])

    def from_query(self, base_query: Query):
        return QueryBuilder(self, base_query)

    def filter(self, query: Query, filters: List[Dict]) -> BinaryExpression:
        return and_(
            self[f["name"]].filter(query, f["values"])
            for f in filters
            if f["name"] in self.keys()
        )


def _init_facet(facet: Union[Type[Facet], Facet, dict, str]) -> Facet:
    if isinstance(facet, type) and issubclass(facet, Facet):
        return facet()
    if isinstance(facet, Facet):
        return facet
    if isinstance(facet, dict):
        return Facet(*facet)
    if isinstance(facet, str):
        return Facet(name=facet)
    raise SQLAlchemyFacetsError(f"Cannot init facet {facet} : wrong type")


def declare_facets(*args: Union[Type[Facet], Facet, Dict, str]) -> Config:
    return Config(facets=[_init_facet(f) for f in args])


class QueryBuilder:

    def __init__(self, config: Config, base_query: Query):
        self.facets = config
        self.base = base_query.subquery()
        self.session = base_query.session

    @property
    def query(self) -> Query:
        facet_columns = [f.facet_column(self.base) for f in self.facets.values()]
        count_field = get_pk(self.base)
        count_column = labeled_column_from_name_on_base(self.base, count_field)

        return self.session\
            .query(*[
                *facet_columns,
                func.count(distinct(count_column))
            ]) \
            .group_by(func.grouping_sets(*facet_columns))

    def all(self) -> List[FacetResult]:
        return self.formatter(
            self.query.all() if self.facets else [()]
        )

    def formatter(self, raw_result: List[Tuple]) -> List[FacetResult]:
        raw_facets = list(zip(*raw_result)) or [()] * (len(self.facets)+1)

        return [
            FacetResult.from_dual_sequences(
                facet=facet,
                values=raw_facets[i],
                counts=raw_facets[-1]
            )
            for i, facet in enumerate(self.facets.values())
        ]


def labeled_column_from_name_on_base(base: Selectable, name: str):
    return getattr(base.c, name).label(name)


def labeled_column_from_name_on_query(query: Query, name: str):
    for entity in query._entities:
        if isinstance(entity, _MapperEntity):
            for e in entity.entities:
                if hasattr(e, name):
                    return getattr(e, name)
        if isinstance(entity, _ColumnEntity) and \
                entity.column.name == name:
            return entity.column
    raise SQLAlchemyFacetsError(f"No field '{name}' on query '{query}'")


def get_pk(base: Selectable) -> str:
    for column in base.columns:
        if column.primary_key:
            return column.name
    raise SQLAlchemyFacetsError(f"Could not find any primary key on '{base}'")
