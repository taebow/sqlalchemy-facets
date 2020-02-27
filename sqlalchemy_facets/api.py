from typing import Sequence, Union

from sqlalchemy.orm import Query
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy import and_

from .query import FacetsQuery
from .facet import build_facets


def get_facets(query: Query, facets: Union[dict, Sequence[str]]) -> FacetsQuery:
    return FacetsQuery(
        query=query,
        facets=build_facets(facets)
    )


def get_filter(query: Query, facets: Union[dict, Sequence[str]], selection: dict) -> BinaryExpression:
    facets = build_facets(facets)
    return and_(
        facets[name].filter(query, values)
        for name, values in selection.items()
        if name in facets.keys()
    )
