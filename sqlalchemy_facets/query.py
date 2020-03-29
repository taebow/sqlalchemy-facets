from typing import List, Tuple
from functools import wraps
from collections import OrderedDict

from sqlalchemy.orm import Query
from sqlalchemy import func, distinct, tuple_

from .facet import Facet
from .types import FacetedResult, FacetResult, Bucket
from .utils import get_column, get_primary_key, translate_grouping


# noinspection PyDefaultArgument
def setup_query_columns(facets, col_names=None, result=None):
    col_names, result = col_names or [], result or []
    for facet in facets:
        if facet.name in col_names:
            facet.col_index = col_names.index(facet.name)
        else:
            col_names.append(facet.name)
            result.append(facet)
            facet.col_index = len(col_names)-1

        setup_query_columns(facet.children, col_names, result)

    return result

# noinspection PyDefaultArgument
def setup_grouping_index(facets, col_count: int, grouping_index=None,
                         sets=None):
    grouping_index, sets = grouping_index or dict(), sets or set()
    for facet in facets:
        base_grouping = facet.parent.grouping if facet.parent else []
        facet.grouping = base_grouping + [facet.col_index]
        index_value = translate_grouping(facet.grouping, col_count)
        sets.add(frozenset(x for x in facet.grouping))

        if index_value not in grouping_index.keys():
            grouping_index[index_value] = [facet]
        else:
            grouping_index[index_value].append(facet)

        setup_grouping_index(facet.children, col_count, grouping_index, sets)

    return grouping_index, sets

def sub_facets(facets):
    facets_by_name = OrderedDict()
    for name, facet_instance in facets.items():
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
            for f in self._column_facets
        ]
        count_field = get_primary_key(base)
        count_column = get_column(base, count_field)
        grouping_sets = []
        for s in self._sets:
            grouping_sets.append(
                self._column_facets[next(iter(s))].facet_column(base)
                if len(s) == 1 else
                tuple_(*[self._column_facets[i].facet_column(base) for i in s])
            )


        return self.session.query(
            *[
                *facet_columns,
                func.grouping(*facet_columns),
                func.count(distinct(count_column))
            ]
        ).group_by(func.grouping_sets(*grouping_sets))


    def facets(self):
        return self.formatter(
            self.facets_query() if self._column_facets else []
        )


    def formatter(self, raw_results: List[Tuple]) -> List[FacetResult]:
        result = OrderedDict()
        for raw_result in raw_results:
            facets = self._grouping_index[raw_result[-2]]
            for facet in facets:
                facet_result = facet.get_or_create_facet_result(result, raw_result)
                facet_result._buckets[raw_result[facet.col_index]] = Bucket(
                    value=facet.mapper[raw_result[facet.col_index]],
                    count=raw_result[-1]
                )
        return list(result.values())

    def all(self):
        return FacetedResult(
            base_result=self.base.all(),
            facets=self.facets()
        )



