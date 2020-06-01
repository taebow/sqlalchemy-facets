from collections import Counter
import pytest

from .conftest import QUERIES

from sqlalchemy_facets import FacetedQuery, RangeFacet, FacetResult, Bucket


class FacetedBlog(FacetedQuery):

    id = RangeFacet(
        (0, 10),
        (10, 20),
        (15, 35),
    )



@pytest.mark.parametrize("query", QUERIES)
def test_return_types(query):
    faceted_query = FacetedBlog(query)
    facets = faceted_query.all().facets

    assert len(facets) == 1
    for facet in faceted_query.all().facets:
        assert isinstance(facet, FacetResult)
        assert len(facet.buckets) > 0
        for bucket in facet.buckets:
            assert isinstance(bucket, Bucket)


@pytest.mark.parametrize("query", QUERIES)
def test_buckets_count(query):
    faceted_query = FacetedBlog(query)
    faceted_result = faceted_query.all()

    assert len(faceted_result.facets) > 0
    for facet in faceted_result.facets:
        result_values = [getattr(r, facet.name) for r in faceted_result]
        print(len(facet.buckets))
        for bucket in facet.buckets:
            low, high = [int(v) for v in bucket.value.split("-")]
            assert bucket.count == len([res for res in result_values if low <= res < high])
