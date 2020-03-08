from functools import wraps
from collections import OrderedDict

from sqlalchemy.orm import Query

from .facet import Facet
from .types import FacetedResult


class FacetedQueryMeta(type):

    def __init__(cls, classname, bases, dict_):
        cls.setup_facets(cls, cls.__dict__)
        type.__init__(cls, classname, bases, dict_)

    @staticmethod
    def setup_facets(cls, dict_):
        setattr(cls, "facets", OrderedDict())
        for k, class_attribute in dict_.items():
            if isinstance(class_attribute, Facet):
                cls.facets[k] = class_attribute
                class_attribute.name = k


class FacetedQuery(metaclass=FacetedQueryMeta):

    def __init__(self, query: Query):
        self.base = query


    def __getattr__(self, item):
        fn = getattr(self.base, item)
        @wraps(fn)
        def wrapped(*args, **kwargs):
            self.base = fn(*args, **kwargs)
            return self
        return wrapped


    def all(self):
        return FacetedResult(self.base.all())



