from typing import NamedTuple, Any, List


class Bucket(NamedTuple):

    value: Any
    count: int


class FacetResult(NamedTuple):

    name: str
    buckets: List[Bucket]


class FacetedResult(list):
    pass