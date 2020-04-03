from random import choice

import pytest

from .fixtures import Post, categories, Author
from .conftest import QUERIES

from sqlalchemy_facets import FacetedQuery, TermsFacet

class FacetedBlog(FacetedQuery):

    category = TermsFacet()


@pytest.mark.parametrize("query", QUERIES)
def test_query_accessibility_one_filter(query):
    faceted_query = FacetedBlog(query)
    filter = Post.category == choice(categories)

    query = query.filter(filter)
    faceted_query = faceted_query.filter(filter)

    assert isinstance(faceted_query, FacetedQuery)
    assert query.all() == faceted_query.all()


@pytest.mark.parametrize("query", QUERIES)
def test_query_accessibility_two_filters(query):

    faceted_query = FacetedBlog(query)
    filters = [
        Post.category == choice(categories)
        for _ in range(2)
    ]

    for filter in filters:
        query = query.filter(filter)
        faceted_query = faceted_query.filter(filter)

    assert isinstance(faceted_query, FacetedQuery)
    assert query.all() == faceted_query.all()


@pytest.mark.parametrize("query", QUERIES)
def test_query_accessibility_on_join(query):

    faceted_query = FacetedBlog(query)

    query = query.join(Author)
    faceted_query = faceted_query.join(Author)

    assert isinstance(faceted_query, FacetedQuery)
    assert query.all() == faceted_query.all()
