from abc import ABC
from ..mapper import Mapper, IdentityMapper
from ..utils import SQLAlchemyFacetsError
from ..types import FacetResult

class Facet(ABC):

    def __init__(self, *args, **kwargs):
        self._name = None
        self.column_name = None
        self.mapper = IdentityMapper()
        self.children = []
        self.parent = None

        for arg in args:
            if isinstance(arg, str):
                self.column_name = arg

        for k, v in kwargs.items():

            if isinstance(v, Facet):
                self.children.append(v)
                v.name = k
                v.parent = self

            if k == "mapper":
                if isinstance(v, Mapper):
                    self.mapper = v
                elif isinstance(v, dict):
                    self.mapper = IdentityMapper(v)
                else:
                    raise SQLAlchemyFacetsError(
                        f"Bad type for mapper '{str(v)}' ({type(v)})"
                    )
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        if not self.column_name:
            self.column_name = value

    def facet_column(self, base):
        raise NotImplementedError

    def setup_index(self, index):
        self.col_index = index
        if self.parent:
            self.grouping_index = self.parent.grouping_index + [index]
        else:
            self.grouping_index = [index]

    def get_or_create_facet_result(self, root, raw_result):
        if self.parent:
            parent_fr = \
                self.parent.get_or_create_facet_result(root, raw_result)
            parent_bucket = parent_fr._buckets[raw_result[self.parent.col_index]]
            if self.name not in parent_bucket._children.keys():
                facet_result = FacetResult(name=self.name)
                parent_bucket._children[self.name] = facet_result
            else:
                facet_result = parent_bucket._children[self.name]
            return facet_result
        else:
            if self.name not in root.keys():
                facet_result = FacetResult(name=self.name)
                root[self.name] = facet_result
            else:
                facet_result = root[self.name]
            return facet_result