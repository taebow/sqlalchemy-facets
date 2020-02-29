from typing import Sequence, NamedTuple

from .facet import Facet


class ValueCount(NamedTuple):
    value: str
    count: int


class FacetResult:
    def __init__(self, facet: Facet, values_count: Sequence[ValueCount]):
        self.facet = facet
        self.values_count = values_count

    @classmethod
    def from_dual_sequences(
        cls, facet: Facet, values: Sequence, counts: Sequence
    ) -> "FacetResult":

        return cls(
            facet=facet,
            values_count=sorted(
                [
                    ValueCount(value=facet.mapper.transform(v), count=counts[i])
                    for i, v in enumerate(values)
                    if v is not None
                ],
                key=lambda v: v.count,
                reverse=True,
            ),
        )

    def asdict(self) -> dict:
        return {"buckets": [v._asdict() for v in self.values_count]}
