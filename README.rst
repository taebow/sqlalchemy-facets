=================
SQLAlchemy-Facets
=================

.. image:: https://travis-ci.org/tteaka/sqlalchemy-facets.svg?branch=master
   :target: https://travis-ci.org/tteaka/sqlalchemy-facets

SQLAlchemy-Facets is an utility based on `SQLAlchemy`_ that aims to provide
easy-to-use and efficient helpers to build category based filters and do search
with multiple criterias.

Its purpose is to be similar to ElasticSearch's feature `terms aggregation`_.

.. image:: https://i.ibb.co/ZLHxGDv/work-in-progress.png
   :width: 100pt


Installing
----------

Install and update using `pip`_:

.. code-block:: text

  $ pip install -U sqlalchemy-facets


A Simple Example
----------------

Model definition
~~~~~~~~~~~~~~~~

.. code-block:: python

    class Post(Base):
        id = Column(Integer, primary_key=True)
        name = Column(String)
        category = Column(String)
        author = Column(String)


Configuration
~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

    from sqlalchemy_facets import FacetedQuery

    class FacetedBlog(FacetedQuery)

        category = TermsFacet()

        author = TermsFacet(
            limit=10,
            order_by=desc("count")
        )


Facets result
~~~~~~~~~~~~~

.. code-block:: python

    >>> pprint(faceted_posts.all().facets)
    [
        FacetResult(
            name="category",
            buckets=[
                Bucket(value="database", count=5),
                Bucket(value="system", count=7)
            ]
        ),
        FacetResult(
            name="author",
            buckets=[
                Bucket(value="Thibaut Frain" count=12),
                Bucket(value="Guest", count=1)
            ]
        )
    ]


Query API accessibility
~~~~~~~~~~~~~~~~~~~~~~~

A faceted query is just a wrapper around an sqlalchemy query.

Operators like joins and filter are seemlessly applied to the original query.

.. code-block:: python

    posts = session.query(Post)
    faceted_posts = FacetedBlog(posts)

    posts.all() == faceted_posts.all() # => True

    posts.filter(...).all() == faceted_posts.filter(...).all() # => True


Filter helper
~~~~~~~~~~~~~

Let's query only database related posts

.. code-block:: python

    database_posts = faceted_posts\
        .facets_filter({
            "category": ["database"]
        })\
        .all()

    pprint(database_posts.facets)
    [
        FacetResult(
            name="category",
            buckets=[
                Bucket(value="database", count=5),
            ]
        ),
        FacetResult(
            name="author",
            buckets=[
                Bucket(value="Thibaut Frain" count=4),
                Bucket(value="Guest", count=1)
            ]
        )
    ]


Links
-----

-   Code: https://github.com/tteaka/sqlalchemy-facets

.. _SQLAlchemy: https://www.sqlalchemy.org
.. _pip: https://pip.pypa.io/en/stable/quickstart/
.. _terms aggregation: https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-terms-aggregation.html