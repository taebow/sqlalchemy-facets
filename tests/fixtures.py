from sqlalchemy import Column, Integer, String, ForeignKey
from factory import Faker
from factory.alchemy import SQLAlchemyModelFactory

from sqlalchemy_facets import Facet

from .db import session, Base

join_keys = ("jkl", "mno", "pqr", "stu")


class SimpleModelOne(Base):
    __tablename__ = "simple_one"
    id = Column(Integer, primary_key=True)
    str_attribute_one = Column(String)
    str_attribute_two = Column(String, ForeignKey("simple_two.str_attribute_two"))
    int_attribute = Column(Integer)


class SimpleModelTwo(Base):
    __tablename__ = "simple_two"
    str_attribute_two = Column(String, primary_key=True)
    str_attribute_three = Column(String)


class SimpleFactoryOne(SQLAlchemyModelFactory):
    class Meta:
        model = SimpleModelOne
        sqlalchemy_session = session

    str_attribute_one = Faker("random_element", elements=("abc", "def", "ghi"))
    str_attribute_two = Faker("random_element", elements=join_keys)
    int_attribute = Faker("random_element", elements=(123, 987))


def get_simple_two_instances():
    name = Faker("name")
    return [
        SimpleModelTwo(
            str_attribute_two=jk,
            str_attribute_three=name.generate()
        ) for jk in join_keys
    ]


class FacetOne(Facet):
    name = "str_attribute_one"


class FacetTwo(Facet):
    name = "str_attribute_two"


class FacetThree(Facet):
    name = "int_attribute"
