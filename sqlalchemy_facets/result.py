from __future__ import annotations
from typing import Any
from collections import OrderedDict

class FacetResultContainer:

    def __init__(self):
        self._facet_results = OrderedDict()

    def get_facet_result(self, name):
        if name not in self._facet_results.keys():
            self._facet_results[name] = FacetResult(name)
        return self._facet_results[name]

    @property
    def facet_results(self):
        return list(self._facet_results.values())


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


class FacetedResult(list):

    def __init__(self, base_result, raw_faceted_result, grouping_index):
        super().__init__(base_result)
        self.facets = self.build_result(raw_faceted_result, grouping_index)

    @classmethod
    def build_result(cls, raw_faceted_result, grouping_index):
        result = FacetResultContainer()
        cache = dict()
        for result_row in raw_faceted_result:
            for facet in grouping_index[result_row[-2]]:
                value = facet.mapper[result_row[facet.col_index]]
                cls._get_facet_result(
                    facet, result_row, cache, result
                ).add_bucket(
                    Bucket(
                        value=value,
                        count=result_row[-1]
                    )
                )
        return result.facet_results

    @classmethod
    def _get_facet_result(cls, facet, result_row, cache, result):
        key = facet.result_key(result_row)

        if key not in cache.keys():
            if facet.parent:
                container = cls._get_facet_result(
                    facet.parent, result_row, cache, result
                ) \
                .get_bucket(result_row[facet.parent.col_index])

            else:
                container = result

            cache[key] = container.get_facet_result(facet.name)

        return cache[key]