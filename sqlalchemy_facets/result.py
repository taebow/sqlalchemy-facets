from __future__ import annotations
from typing import Any
from collections import OrderedDict


class FacetResultContainer:

    def __init__(self, raw_faceted_result=None, grouping_index=None):
        self._facet_results = OrderedDict()
        if raw_faceted_result and grouping_index:
            self.build_result(raw_faceted_result, grouping_index)

    @property
    def facets(self):
        return list(self._facet_results.values())

    def build_result(self, raw_faceted_result, grouping_index):
        cache = dict()
        for result_row in raw_faceted_result:
            for facet in grouping_index[result_row[-2]]:
                bucket = Bucket(
                    value=facet.mapper[result_row[facet.col_index]],
                    count=result_row[-1]
                )
                self.get_facet_result(
                    facet, result_row, cache
                ).add_bucket(bucket)

    def get_facet_result(self, facet, result_row, cache):
        key = facet.result_key(result_row)

        if key not in cache.keys():
            if facet.parent:
                container = self.get_facet_result(
                    facet.parent, result_row, cache
                ).get_bucket(result_row[facet.parent.col_index])

            else:
                container = self

            if facet.name not in container._facet_results.keys():
                container._facet_results[facet.name] = FacetResult(facet.name)

            cache[key] = container._facet_results[facet.name]

        return cache[key]


class Bucket(FacetResultContainer):

    def __init__(self, value: Any, count: int):
        super().__init__()
        self.value = value
        self.count = count


class FacetResult:

    def __init__(self, name: str):
        self.name = name
        self._buckets = OrderedDict()

    @property
    def buckets(self):
        return list(self._buckets.values())

    def add_bucket(self, bucket):
        self._buckets[bucket.value] = bucket

    def get_bucket(self, value):
        return self._buckets[value]


class FacetedResult(list, FacetResultContainer):

    def __init__(self, base_result, raw_faceted_result, grouping_index):
        list.__init__(self, base_result)
        FacetResultContainer.__init__(
            self, raw_faceted_result, grouping_index
        )
