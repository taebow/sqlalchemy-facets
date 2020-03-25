from typing import List, Tuple
from functools import wraps
from collections import OrderedDict

from sqlalchemy.orm import Query
from sqlalchemy import func, distinct

from .facet import Facet
from .types import FacetedResult, FacetResult
from .utils import get_column, get_primary_key


def sub_facets(facets):
    facets_by_name = OrderedDict()
    for name, facet_instance in facets.items():
        if isinstance(facet_instance, Facet):
            facets_by_name[name] = facet_instance
            facet_instance.name = name
    return facets_by_name


class FacetedQueryMeta(type):

    def __init__(cls, classname, bases, dict_):
        setattr(cls, "_facets", sub_facets(cls.__dict__))
        type.__init__(cls, classname, bases, dict_)


class FacetedQuery(metaclass=FacetedQueryMeta):

    def __init__(self, query: Query):
        self.base = query


    def __getattr__(self, item):
        base_item = getattr(self.base, item)
        if not callable(base_item):
            return base_item

        @wraps(base_item)
        def wrapped(*args, **kwargs):
            self.base = base_item(*args, **kwargs)
            return self
        return wrapped


    def facets_query(self):
        base = self.base.cte()
        facet_columns = [
            f.facet_column(base)
            for f in self._facets.values()
        ]
        count_field = get_primary_key(base)
        count_column = get_column(base, count_field)

        return self.session.query(
            *[*facet_columns, func.count(distinct(count_column))]
        ).group_by(func.grouping_sets(*facet_columns))


    def facets(self):
        return self.formatter(self.facets_query() if self._facets else [()])


    def formatter(self, raw_result: List[Tuple]) -> List[FacetResult]:
        raw_facets = list(zip(*raw_result)) or [()] * (len(self._facets) + 1)

        return [
            FacetResult.from_dual_sequences(
                facet=facet,
                values=raw_facets[i],
                counts=raw_facets[-1]
            )
            for i, facet in enumerate(self._facets.values())
        ]


    def all(self):
        return FacetedResult(
            base_result=self.base.all(),
            facets=self.facets()
        )



