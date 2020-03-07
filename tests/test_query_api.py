from random import choice

import pytest

from .fixtures import Post, categories, Author
from .conftest import QUERIES

from sqlalchemy_facets import FacetedQuery, TermsFacet

class FacetedBlog(FacetedQuery):

    category = TermsFacet()


@pytest.mark.parametrize("query", QUERIES)
def test_query_accessibility_on_filter(query):

    faceted_query = FacetedBlog(query)
    filter = Post.category == choice(categories)

    assert query.filter(filter).all() == faceted_query.filter(filter).all()


@pytest.mark.parametrize("query", QUERIES)
def test_query_accessibility_on_join(query):

    faceted_query = FacetedBlog(query)

    assert query.join(Author).all() == faceted_query.join(Author).all()


