from typing import NamedTuple, Any
from collections import OrderedDict

class Bucket:

    def __init__(self, value: Any, count: int):
        self.value = value
        self.count = count
        self._children = OrderedDict()

    @property
    def children(self):
        return list(self._children.values())


class FacetResult:

    def __init__(self, name: str):
        self.name = name
        self._buckets = OrderedDict()

    @property
    def buckets(self):
        return list(self._buckets.values())


class FacetedResult(list):

    def __init__(self, base_result, facets):
        super().__init__(base_result)
        self.facets = facets
