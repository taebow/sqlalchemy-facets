import pytest

from sqlalchemy_facets import declare_facets
from sqlalchemy_facets import get_facets

from .conftest import FACETS, QUERIES, SEEDS


@pytest.mark.parametrize("facets_list", FACETS)
@pytest.mark.parametrize("query", QUERIES)
@pytest.mark.parametrize("seeds", SEEDS, indirect=True)
def test_declare_count(seeds, query, facets_list):

    get_facets = declare_facets(*facets_list)

    facets_results = get_facets(query).all()
    result = query.all()
    model, size = seeds

    assert len(facets_results) == len(facets_list)

    for facet, facet_result in zip(facets.values(), facets_results):
        assert sum([vc.count for vc in facet_result.values_count]) == len(result) <= size

        for value_count in facet_result.values_count:
            result_count = len(list(filter(
                lambda inst: getattr(inst, facet.name) == value_count.value,
                result
            )))
            assert result_count == value_count.count


@pytest.mark.parametrize("facets_list", FACETS)
@pytest.mark.parametrize("query", QUERIES)
@pytest.mark.parametrize("seeds", SEEDS, indirect=True)
def test_declare_filter(seeds, query, facets_list):
    facets = declare_facets(*facets_list)

    facets_results = facets.from_query(query).all()

    for facet_result in facets_results:
        for value_count in facet_result.values_count:
            new_filter = [{"name": facet_result.facet.name, "values": [value_count.value]}]
            facets_filter = facets.filter(query, new_filter)
            assert len(query.filter(facets_filter).all()) == value_count.count


@pytest.mark.parametrize("facets_list", FACETS)
@pytest.mark.parametrize("query", QUERIES)
@pytest.mark.parametrize("seeds", SEEDS, indirect=True)
def test_get_facets_count(seeds, query, facets_list):

    facets = get_facets(query, facets=facets_list).all()
    result = query.all()
    model, size = seeds

    assert len(facets) == len(facets_list)

    for facet, facet_result in zip(facets.values(), facets):
        assert sum([vc.count for vc in facet_result.values_count]) == len(result) <= size

        for value_count in facet_result.values_count:
            result_count = len(list(filter(
                lambda inst: getattr(inst, facet.name) == value_count.value,
                result
            )))
            assert result_count == value_count.count


@pytest.mark.parametrize("facets_list", FACETS)
@pytest.mark.parametrize("query", QUERIES)
@pytest.mark.parametrize("seeds", SEEDS, indirect=True)
def test_get_facets_filter(seeds, query, facets_list):
    facets = declare_facets(*facets_list)

    facets_results = facets.from_query(query).all()

    for facet_result in facets_results:
        for value_count in facet_result.values_count:
            new_filter = [{"name": facet_result.facet.name, "values": [value_count.value]}]
            facets_filter = facets.filter(query, new_filter)
            assert len(query.filter(facets_filter).all()) == value_count.count


