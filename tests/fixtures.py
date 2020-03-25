from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from factory import Faker
from factory.alchemy import SQLAlchemyModelFactory

from .db import session, Base

authors = [Faker("name").generate() for _ in range(3)]
categories = ["system", "database", "api"]

class Author(Base):
    __tablename__ = "author"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    @classmethod
    def create_all(cls):
        session.add_all([Author(name=name) for name in authors])


class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    category = Column(String)
    author_id = Column(Integer, ForeignKey(Author.id))
    published = Column(Boolean)
    author = relationship(Author)



class PostFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Post
        sqlalchemy_session = session

    name = Faker("sentence")
    category = Faker("random_element", elements=categories)
    author_id = Faker(
        "random_element", elements=[i for i in range(1, len(authors)+1)]
    )
    published = Faker("random_element", elements=[True, False])