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


def check_children_occurence(result_container, n_facets):
    n_facets = [n_facets] if isinstance(n_facets, int) else n_facets
    assert len(result_container.facets) == n_facets[0]
    for i, facet_result in enumerate(result_container.facets):
        assert len(facet_result.buckets) > 0
        for bucket in facet_result.buckets:
            if n_facets[1:]:
                check_children_occurence(bucket, n_facets[1:][i])


def check_types(result_container):
    for facet_result in result_container.facets:
        assert isinstance(facet_result, FacetResult)
        for bucket in facet_result.buckets:
            assert isinstance(bucket, Bucket)
            check_types(bucket)


def check_values(result_container, faceted_result=None, cond=lambda _: True):
    faceted_result = faceted_result or result_container
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
                and cond(r)
            )


def check_count(result_container, faceted_result=None, cond=lambda _: True):
    faceted_result = faceted_result or result_container
    for facet in result_container.facets:
        result_counter = Counter(
            getattr(r, facet.name)
            for r in faceted_result
            if cond(r)
        )
        for bucket in facet.buckets:
            assert bucket.count == result_counter[bucket.value]
            check_count(
                bucket, faceted_result,
                cond=lambda r: getattr(r, facet.name) == bucket.value
                and cond(r)
            )
        assert sum(b.count for b in facet.buckets) == \
            sum(result_counter.values())


@pytest.mark.parametrize("query", QUERIES)
def test_return_types(query):
    faceted_query = FacetedBlog(query)
    faceted_result = faceted_query.all()

    check_children_occurence(faceted_result, [2, [1, 1], 1])
    check_types(faceted_result)


@pytest.mark.parametrize("query", QUERIES)
def test_buckets_value(query):
    faceted_query = FacetedBlog(query)
    faceted_result = faceted_query.all()

    check_values(faceted_result)


@pytest.mark.parametrize("query", QUERIES)
def test_buckets_count(query):
    faceted_query = FacetedBlog(query)
    faceted_result = faceted_query.all()

    check_count(faceted_result)
