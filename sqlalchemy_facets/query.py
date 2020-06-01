from functools import wraps
from collections import OrderedDict

from sqlalchemy.orm import Query
from sqlalchemy import func, distinct, tuple_, desc

from .facet import Facet
from .result import FacetedResult, FacetResultContainer
from .utils import get_column, get_primary_key


def setup_query_columns(facets, col_names=None, result=None):
    col_names, result = col_names or [], result or []
    for facet in facets:
        if facet.name not in col_names:
            col_names.append(facet.name)
            result.append(facet)
        facet.setup(col_names.index(facet.name))

    for facet in facets:
        setup_query_columns(facet.children, col_names, result)

    return result


def setup_grouping_index(facets, col_count: int, grouping_index=None,
                         sets=None):
    grouping_index, sets = grouping_index or dict(), sets or set()
    for facet in facets:
        sets.add(frozenset(x for x in facet.grouping))
        key = facet.grouping_key(col_count)

        if key in grouping_index.keys():
            grouping_index[key].append(facet)
        else:
            grouping_index[key] = [facet]

        setup_grouping_index(facet.children, col_count, grouping_index, sets)

    return grouping_index, sets


def sub_facets(facets):
    facets_by_name = OrderedDict()
    for name, facet_instance in reversed(facets.items()):
        if isinstance(facet_instance, Facet):
            facets_by_name[name] = facet_instance
            facet_instance.name = name
    return facets_by_name


class FacetedQueryMeta(type):

    def __init__(cls, classname, bases, dict_):
        root_facets = sub_facets(dict_)
        column_facets = setup_query_columns(root_facets.values())
        grouping_index, sets = setup_grouping_index(
            root_facets.values(), len(column_facets)
        )
        setattr(cls, "_root_facets", root_facets)
        setattr(cls, "_column_facets", column_facets)
        setattr(cls, "_sets", sets)
        setattr(cls, "_grouping_index", grouping_index)
        type.__init__(cls, classname, bases, dict_)


class FacetedQuery(metaclass=FacetedQueryMeta):

    def __init__(self, query: Query):
        self.base = query.limit(None).offset(None)

    def __getattr__(self, item):
        base_item = getattr(self.base, item)
        if not callable(base_item):
            return base_item

        @wraps(base_item)
        def wrapped(*args, **kwargs):
            self.base = base_item(*args, **kwargs)
            return self
        return wrapped

    @property
    def facets_query(self):
        base = self.base.cte()

        # Get facets columns
        facet_columns = [
            f.facet_column(base)
            for f in self._column_facets
        ]

        # Get count column
        count_field = get_primary_key(base)
        count_column = get_column(base, count_field)

        # Grouping sets columns
        grouping_sets = [
            self._column_facets[next(iter(s))].facet_column(base)
            if len(s) == 1 else
            tuple_(*[
                self._column_facets[i].facet_column(base)
                for i in s
            ])
            for s in self._sets
        ]

        grouping_col = func.grouping(*facet_columns).label("_grouping")

        facets_query = self.session.query(
            *facet_columns,
            grouping_col,
            func.count(distinct(count_column))
        )

        for facet in self._column_facets:
            facets_query = facet.apply_join(base, facets_query)

        return facets_query \
            .group_by(func.grouping_sets(*grouping_sets))\
            .order_by(desc(grouping_col))

    def facets(self):
        return FacetResultContainer(
            self.facets_query.all(),
            self._grouping_index
        ).facets

    def all(self):
        print(self.facets_query)
        return FacetedResult(
            base_result=self.base.all(),
            raw_faceted_result=self.facets_query.all(),
            grouping_index=self._grouping_index
        )
