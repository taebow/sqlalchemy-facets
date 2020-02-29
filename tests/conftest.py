import pytest

from .db import session, Base, engine
from .fixtures import SimpleModelOne, \
    SimpleModelTwo, SimpleFactoryOne, get_simple_two_instances


@pytest.fixture(scope="module", autouse=True)
def reset():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session.add_all(get_simple_two_instances())
    session.commit()
    yield
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def seeds(request):
    factory, size = request.param
    factory.create_batch(size)
    yield factory, size
    session.rollback()


FACETS = [
    ["str_attribute_one"],
    ["str_attribute_one", "str_attribute_two"],
    [],
    {"custom_name_one": {"column_name": "str_attribute_one"}}
]

SUBQUERY = session.query(SimpleModelOne)\
    .filter(SimpleModelOne.int_attribute > 500)\


QUERIES = [
    session.query(SimpleModelOne),
    session.query(SimpleModelOne).filter(SimpleModelOne.int_attribute > 500),
    session.query(SimpleModelOne).filter(SimpleModelOne.str_attribute_one.in_(["abc", "def"])),
    session.query(SimpleModelOne.id, SimpleModelOne.str_attribute_one,
                  SimpleModelOne.str_attribute_two, SimpleModelOne.int_attribute),
    session.query(SUBQUERY.subquery()),
    session.query(SUBQUERY.cte()),
    session.query(SimpleModelOne).join(SimpleModelTwo)
]

SEEDS = [
    (SimpleFactoryOne, 0),
    (SimpleFactoryOne, 1),
    (SimpleFactoryOne, 23),
    (SimpleFactoryOne, 100)
]