from .base import Facet

class TermsFacet(Facet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def facet_column(self, base):
        return getattr(base.c, self.column_name).label(self.column_name)