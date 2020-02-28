=================
SQLAlchemy-Facets
=================

.. image:: https://travis-ci.org/tteaka/sqlalchemy-facets.svg?branch=master
   :target: https://travis-ci.org/tteaka/sqlalchemy-facets

SQLAlchemy-Facets is an utility based on `SQLAlchemy`_ that aims to provide
easy-to-use and efficient helpers to build category based filters and do search
with multiple criterias.

.. image:: https://ibb.co/dWbDjYX
   :width: 40pt


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

    class Movie(Base):
        id = Column(Integer, primary_key=True)
        name = Column(String)
        genre = Column(String)
        language = Column(String)


Configuration
~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

    from sqlalchemy_facets import declare_facets

    f = declare_facets("genre", "language")

Querying
~~~~~~~~
.. code-block:: python

    # Main query
    all_movies = session.query(Movie)

    # Facets query
    facets = f.get_facets(all_movies)


Result
~~~~~~

.. code-block:: python

    >>> pprint(facets)
    {
        "genre" {
            "buckets": [
                {"value": "horror", "count": 23},
                {"value": "action", "count": 52},
                {"value": "comedy", "count": 34}
            ]
        },
        "language": {
            "buckets": [
                {"value": "English", "count": 75},
                {"value": "Spanish", "count": 12},
                {"value": "French", "count" 23}
            ]
        }
    }


Filter
~~~~~~

.. code-block:: python

    >>> selection = [
    >>>     {"genre": {"values": ["action", "comedy"]}},
    >>>     {"language": {"values" ["Spanish", "French"]}}
    >>> ]
    >>> print("Let's query French or Spanish, action or comedy movies !")
    >>> f.apply_filter(all_movies, selection).all()


Links
-----

-   Code: https://github.com/tteaka/sqlalchemy-facets

.. _SQLAlchemy: https://www.sqlalchemy.org
.. _pip: https://pip.pypa.io/en/stable/quickstart/