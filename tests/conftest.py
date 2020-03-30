from random import choice

import pytest

from .db import session, Base, engine
from .fixtures import Author, Post, PostFactory, categories

@pytest.fixture(scope="session", autouse=True)
def tables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="session", autouse=True)
def data(tables):
    Author.create_all()
    PostFactory.create_batch(77)
    session.commit()


subquery = session.query(Post).filter(Post.category == choice(categories))

QUERIES = [
    session.query(Post),
    session.query(Post).filter(Post.category == choice(categories)),
    session.query(Post.id, Post.name, Post.category, Post.author_id, Post.published),
    session.query(subquery.subquery()),
    session.query(subquery.cte()),
]
