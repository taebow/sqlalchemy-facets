from typing import NamedTuple, Any, List, Sequence

from .facet import Facet

class Bucket(NamedTuple):

    value: Any
    count: int


class FacetResult(NamedTuple):

    name: str
    buckets: List[Bucket]


    @staticmethod
    def from_dual_sequences(facet: Facet, values: Sequence,
                            counts: Sequence) -> "FacetResult":
        return FacetResult(
            name=facet.name,
            buckets=sorted(
                [
                    Bucket(
                        value=facet.mapper[v],
                        count=counts[i]
                    )
                    for i, v in enumerate(values)
                    if v is not None
                ],
                key=lambda v: v.count,
                reverse=True,
            )
        )


class FacetedResult(list):

    def __init__(self, base_result, facets):
        super().__init__(base_result)
        self.facets = facets
