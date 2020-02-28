from typing import Sequence, Union, Dict

from sqlalchemy.orm import Query
from sqlalchemy import and_

from .facet import build_facets
from .query import QueryBuilder


class FacetsDeclaration:
    def __init__(self, facets: Union[Dict[str, dict], Sequence[str]] = None):
        self.facets = build_facets(facets or [])

    def get_facets(
        self, query: Query, facets: Union[Dict[str, dict], Sequence[str]] = None
    ) -> Dict[str, dict]:
        self.facets = build_facets(facets) if facets else self.facets
        return QueryBuilder(query, self.facets).all()

    def apply_filters(self, query: Query, selection: dict) -> Query:
        return query.filter(
            and_(
                self.facets[name].filter(query, filter_config)
                for name, filter_config in selection.items()
                if name in self.facets.keys()
            )
        )


def declare_facets(
    facets: Union[Dict[str, dict], Sequence[str]] = None
) -> FacetsDeclaration:
    return FacetsDeclaration(facets)


f = declare_facets()
