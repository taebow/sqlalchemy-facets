import pytest

from sqlalchemy_facets.utils import translate_grouping


@pytest.mark.parametrize("pos, len, grouping", [
    ([2], 3, 6),
    ([1], 3, 5),
    ([1, 2], 3, 4),
    ([0], 3, 3),
    ([0, 2], 3, 2),
    ([0, 1], 3, 1),
    ([0, 1, 2], 3, 0)
])
def test_translate_grouping(pos, len, grouping):
    assert translate_grouping(pos, len) == grouping