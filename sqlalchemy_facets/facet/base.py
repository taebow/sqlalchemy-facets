from abc import ABC

class Facet(ABC):

    def __init__(self, *args, **kwargs):
        self._name = None
        self.column_name = None

        for arg in args:
            if isinstance(arg, str):
                self.column_name = arg

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        if not self.column_name:
            self.column_name = value