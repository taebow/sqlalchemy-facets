import pytest

from .db import session
from .fixtures import Post

from sqlalchemy_facets import FacetedQuery, TermsFacet

published_mapper = {
    True: "Public post",
    False: "Private post"
}


class FacetedBlog(FacetedQuery):

    published = TermsFacet(
        mapper=published_mapper
    )


def test_mapper_values():
    query = session.query(Post)
    faceted_query = FacetedBlog(query)

    facets = faceted_query.facets()
    assert len(facets) == 1

    published_facet =  faceted_query.facets()[0]
    assert len(published_facet.buckets) == 2

    assert {b.value for b in published_facet.buckets} \
           == set(published_mapper.values())


@pytest.mark.parametrize("db_value, outer_value", published_mapper.items())
def test_value_mapping(db_value, outer_value):
    query = session.query(Post).filter(Post.published == db_value)
    faceted_query = FacetedBlog(query)

    published_facet =  faceted_query.facets()[0]

    assert len(published_facet.buckets) == 1

    bucket = published_facet.buckets[0]

    assert query.count() == bucket.count
    assert bucket.value == outer_value
