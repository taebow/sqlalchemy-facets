from random import choice

import pytest

from .db import session, Base, engine
from .fixtures import Author, Post, PostFactory, categories, authors


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
    yield
    session.rollback()


subquery = session.query(Post).filter(Post.category == choice(categories))

QUERIES = [
    session.query(Post),
    session.query(Post).filter(Post.category == choice(categories)),
    session.query(Post.id, Post.name),
    session.query(subquery.subquery()),
    session.query(subquery.cte()),
    session.query(Post).join(Author)
]
