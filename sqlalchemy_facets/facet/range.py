from sqlalchemy import select, literal, union, and_, or_
from .base import Facet


class RangeFacet(Facet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ranges = []
        for arg in args:
            if isinstance(arg, tuple) and len(arg) == 2:
                self.ranges.append(Range(*arg))
        self.subquery = self.build_subquery(self.ranges)

    def facet_column(self, base):
        return self.subquery.c.key.label(self.name)

    def apply_join(self, base, facets_query):
        return facets_query.outerjoin(
            self.subquery,
            and_(
                getattr(base.c, self.column_name) >= self.subquery.c.low,
                or_(
                    getattr(base.c, self.column_name) <= self.subquery.c.high,
                    self.subquery.c.high == None
                )
            )
        )

    @staticmethod
    def build_subquery(ranges):
        return union(
            *[
                select([
                    literal(r.key).label("key"),
                    literal(r.low).label("low"),
                    literal(r.high).label("high")
                ])
                for r in ranges
            ]
        )


class Range:

    def __init__(self, low, high):
        self.low = low
        self.high = high

    @property
    def key(self):
        return f"{self.low}-{self.high}"
