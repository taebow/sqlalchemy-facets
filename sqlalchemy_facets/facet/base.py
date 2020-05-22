from abc import ABC
from ..mapper import Mapper, IdentityMapper
from ..utils import SQLAlchemyFacetsError


class Facet(ABC):

    def __init__(self, *args, **kwargs):
        self._name = None
        self.column_name = None
        self.mapper = IdentityMapper()
        self.children = []
        self.parent = None
        self.grouping = []
        self.col_index = None

        for arg in args:
            if isinstance(arg, str):
                self.column_name = arg

        for k, v in reversed(kwargs.items()):

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

    def setup(self, col_index: int):
        self.col_index = col_index
        self.grouping = getattr(
            self.parent, "grouping", list()
        ) + [col_index]

    def grouping_key(self, col_count):
        return int(
            (2**col_count)*(1-sum([2**(-p-1) for p in self.grouping]))-1
        )

    def result_key(self, result_row: tuple):
        buckets_mask = (
            result_row[index]
            for index in getattr(self.parent, "grouping", ())
        )
        return result_row[-2], *buckets_mask
