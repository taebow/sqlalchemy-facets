SQLAlchemy-Facets
=================

SQLAlchemy-Facets is an utility based on `SQLAlchemy`_ that aims to provide
easy-to-use and efficient helpers to build category based filters and do search
with multiple criterias.

.. warning::
  work in progress


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

    facets = declare_facets("genre", "language")

Querying
~~~~~~~~
.. code-block:: python

    # Main query
    all_movies = session.query(Movie)

    # Facets query
    facets_result = facets.from_query(all_movies).all()


Result
~~~~~~

.. code-block:: python

    >>> pprint(facets_result)
    {
        "name": "genre",
        "values": {
            "value": "horror", "count": 23,
            "value": "action", "count": 52,
            "value": "comedy", "count": 34
        },
        "name": "language",
        "values": {
            "value": "English", "count": 75,
            "value": "Spanish", "count": 12,
            "value": "French", "count" 23
        }
    }


Filter
~~~~~~

.. code-block:: python

    >>> selection = [
    >>>     {"name": "genre", "values": ["action", "comedy"]},
    >>>     {"name": "language", "values" ["Spanish", "French"]}
    >>> ]
    >>> print("Let's query French or Spanish, action or comedy movies !")
    >>> result = facets.filter(all_movies, selection).all()


Links
-----

-   Code: https://github.com/thibautfrain/sqlalchemy-facets

.. _SQLAlchemy: https://www.sqlalchemy.org
.. _pip: https://pip.pypa.io/en/stable/quickstart/