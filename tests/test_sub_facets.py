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

    author_id = TermsFacet(
        published=TermsFacet()
    )


def check_occurences(result_container, n_facets):
    n_facets = [n_facets] if isinstance(n_facets, int) else n_facets
    assert len(result_container.facets) == n_facets[0]
    for i, facet_result in enumerate(result_container.facets):
        print(facet_result.name)
        assert len(facet_result.buckets) > 0
        for bucket in facet_result.buckets:
            if n_facets[1:]:
                check_occurences(bucket, n_facets[1:][i])


def check_types(result_container):
    for facet_result in result_container.facets:
        assert isinstance(facet_result, FacetResult)
        for bucket in facet_result.buckets:
            assert isinstance(bucket, Bucket)
            check_types(bucket)


def check_values(result_container, faceted_result, cond=lambda _: True):
    for facet_result in result_container.facets:
        result_values = [
            getattr(r, facet_result.name)
            for r in faceted_result
            if cond(r)
        ]
        for bucket in facet_result.buckets:
            assert bucket.value in result_values
            check_values(
                bucket, faceted_result,
                cond=lambda r: getattr(r, facet_result.name) == bucket.value
            )


@pytest.mark.parametrize("query", QUERIES)
def test_return_types(query):
    faceted_query = FacetedBlog(query)
    faceted_result = faceted_query.all()

    check_occurences(faceted_result, [2, [1, 1], 1])

    assert len(faceted_result.facets) == 2
    for facet in faceted_result.facets:
        assert isinstance(facet, FacetResult)
        for bucket in facet.buckets:
            assert isinstance(bucket, Bucket)
            for facet2 in bucket.facets:
                assert isinstance(facet2, FacetResult)
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

            for facet2 in bucket.facets:
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
            for facet2 in bucket.facets:
                result_counter2 = Counter([
                    getattr(r2,  facet2.name)
                    for r2 in faceted_result
                    if getattr(r2, facet.name) == bucket.value
                ])

                for bucket2 in facet2.buckets:
                    assert bucket2.count == result_counter2[bucket2.value]

                assert sum(result_counter2.values()) == bucket.count
