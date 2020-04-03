from collections import Counter
import pytest

from .conftest import QUERIES

from sqlalchemy_facets import FacetedQuery, TermsFacet, FacetResult, Bucket

class FacetedBlog(FacetedQuery):

    category = TermsFacet(
        author_id=TermsFacet(
            published=TermsFacet()
        )
    )

    author_id=TermsFacet(
        published=TermsFacet()
    )


@pytest.mark.parametrize("query", QUERIES)
def test_return_types(query):
    faceted_query = FacetedBlog(query)
    facets = faceted_query.all().facets

    assert len(facets) == 2
    for facet in facets:
        assert isinstance(facet, FacetResult)
        assert len(facet.buckets) > 0
        for bucket in facet.buckets:
            assert isinstance(bucket, Bucket)
            assert len(bucket.facet_results) == 1
            for facet2 in bucket.facet_results:
                assert isinstance(facet2, FacetResult)
                assert len(facet2.buckets) > 0
                for bucket2 in facet2.buckets:
                    assert isinstance(bucket2, Bucket)


@pytest.mark.parametrize("query", QUERIES)
def test_buckets_value(query):
    faceted_query = FacetedBlog(query)
    faceted_result = faceted_query.all()

    assert len(faceted_result.facets) > 0
    for facet in faceted_result.facets:
        result_values = [getattr(r, facet.name) for r in faceted_result]

        for bucket in facet.buckets:
            assert bucket.value in result_values

            for facet2 in bucket.facet_results:
                result_values2 = [
                    getattr(r2,  facet2.name)
                    for r2 in faceted_result
                    if getattr(r2, facet.name) == bucket.value
                ]

                for bucket2 in facet2.buckets:
                    assert bucket2.value in result_values2


@pytest.mark.parametrize("query", QUERIES)
def test_buckets_count(query):
    faceted_query = FacetedBlog(query)
    faceted_result = faceted_query.all()

    for facet in faceted_result.facets:
        result_counter = Counter(
            [getattr(r, facet.name) for r in faceted_result]
        )
        for bucket in facet.buckets:
            assert bucket.count == result_counter[bucket.value]
            for facet2 in bucket.facet_results:
                result_counter2 = Counter([
                    getattr(r2,  facet2.name)
                    for r2 in faceted_result
                    if getattr(r2, facet.name) == bucket.value
                ])

                for bucket2 in facet2.buckets:
                    assert bucket2.count == result_counter2[bucket2.value]

                assert sum(result_counter2.values()) == bucket.count