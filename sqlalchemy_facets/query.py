from functools import wraps
from sqlalchemy.orm import Query

class FacetedQuery:

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


class FacetedResult(list):
    pass