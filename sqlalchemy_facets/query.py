from typing import List, Tuple
from collections import OrderedDict

from sqlalchemy import func, distinct
from sqlalchemy.orm import Query

from .facet import Facet
from .formatter import FacetResult
from .utils import get_column, get_primary_key


class FacetsQuery:

    def __init__(self, query: Query, facets: OrderedDict[str, Facet]):
        self.base = query.subquery()
        self.session = query.session
        self.facets = facets

    @property
    def query(self) -> Query:
        facet_columns = [f.facet_column(self.base) for f in self.facets.values()]
        count_field = get_primary_key(self.base)
        count_column = get_column(self.base, count_field)

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
