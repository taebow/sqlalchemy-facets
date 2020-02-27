from typing import Dict, Sequence, Any, Union
from collections import OrderedDict

from sqlalchemy.sql import Selectable
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.sql.elements import Label
from sqlalchemy.orm import Query

from .utils import get_column, SQLAlchemyFacetsError

class Mapper:

    @staticmethod
    def transform(value: Any) -> str:
        return value

    @staticmethod
    def revert(value: str) -> Any:
        return value


class Facet:
    name: str

    def __init__(self, name: str = None, mapper: Mapper = Mapper()):
        self.name = name or self.name
        self.mapper = mapper

    def _labeled_column(self, base: Selectable) -> Label:
        return get_column(base, self.name)

    def facet_column(self, base: Selectable) -> Label:
        return self._labeled_column(base)

    def filter(self, query: Query, values: Sequence) -> BinaryExpression:
        return get_column(query, self.name)\
            .in_([self.mapper.revert(v) for v in values])


def build_facets(facets: Union[Dict[str, dict], Sequence[str]]) -> OrderedDict[str, Facet]:
    if isinstance(facets, list):
        return OrderedDict((name, Facet(name)) for name in facets)
    elif isinstance(facets, dict):
        facet_instances = OrderedDict()
        for name, config in facets.items():
            facet_class = config.get("class", Facet)
            facet_instances[name] = facet_class(**config)
        return facet_instances
    else:
        raise SQLAlchemyFacetsError(
            f"Cannot init facets {facets} : bad format")
