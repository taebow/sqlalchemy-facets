from sqlalchemy.orm import Query

class FacetedQuery:

    def __init__(self, query: Query):
        self.base = query


    def __getattr__(self, name):
        return getattr(self.base, name)


    def all(self):
        return FacetedResult(self.base.all())


class FacetedResult(list):
    pass