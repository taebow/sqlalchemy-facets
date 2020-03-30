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

    def get_facet_result(self, root, raw_result):
        if self.parent:
            print(self.parent.get_facet_result(root, raw_result)._buckets)
            container = self.parent\
                .get_facet_result(root, raw_result)\
                ._buckets[raw_result[self.parent.col_index]]\
                ._children
        else:
            container = root

        if self.name not in container.keys():
            container[self.name] = FacetResult(name=self.name)

        return container[self.name]

    def mask_values(self, raw_result):
        return tuple(raw_result[index] for index in self.grouping)
