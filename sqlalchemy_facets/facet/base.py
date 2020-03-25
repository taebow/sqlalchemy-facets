from abc import ABC
from ..mapper import Mapper, IdentityMapper
from ..utils import SQLAlchemyFacetsError

class Facet(ABC):

    def __init__(self, *args, **kwargs):
        self._name = None
        self.column_name = None
        self.mapper = IdentityMapper()

        for arg in args:
            if isinstance(arg, str):
                self.column_name = arg

        for k, v in kwargs.items():
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