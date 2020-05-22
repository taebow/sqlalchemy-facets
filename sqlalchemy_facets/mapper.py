from abc import ABC


class Mapper(dict, ABC):

    @property
    def reverse(self) -> dict:
        raise NotImplementedError


class IdentityMapper(Mapper):

    def __init__(self, _dict=None, origin=None):
        super().__init__(_dict or dict())
        if origin is None:
            self._reverse = type(self)(
                {v: k for k, v in self.items()},
                origin=self
            )
        else:
            self._reverse = origin

    @property
    def reverse(self) -> dict:
        return self._reverse

    def __missing__(self, key):
        return key
