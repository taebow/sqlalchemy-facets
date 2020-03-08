from random import choice
from collections import Counter
import pytest

from .fixtures import Post, categories, Author
from .conftest import QUERIES

from sqlalchemy_facets import FacetedQuery, TermsFacet, FacetResult, Bucket

class FacetedBlog(FacetedQuery):

    category = TermsFacet()


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
def test_buckets_value(query):
    faceted_query = FacetedBlog(query)
    faceted_result = faceted_query.all()

    assert len(faceted_result.facets) > 0
    for facet in faceted_result.facets:
        assert len(facet.buckets) > 0
        result_values = [getattr(r, facet.name) for r in faceted_result]
        for bucket in facet.buckets:
            assert bucket.value in result_values


@pytest.mark.parametrize("query", QUERIES)
def test_buckets_count(query):
    faceted_query = FacetedBlog(query)
    faceted_result = faceted_query.all()

    assert len(faceted_result.facets) > 0
    for facet in faceted_result.facets:
        assert len(facet.buckets) > 0
        result_counter = Counter(
            [getattr(r, facet.name) for r in faceted_result]
        )
        for bucket in facet.buckets:
            assert bucket.count == result_counter[bucket.value]

