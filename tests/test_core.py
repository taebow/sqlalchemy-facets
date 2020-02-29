import pytest

from sqlalchemy_facets import declare_facets

from .conftest import FACETS, QUERIES, SEEDS


@pytest.mark.parametrize("facets_list", FACETS)
@pytest.mark.parametrize("query", QUERIES)
@pytest.mark.parametrize("seeds", SEEDS, indirect=True)
def test_declare_count(seeds, query, facets_list):

    f = declare_facets(facets_list)

    facets_results = f.get_facets(query)
    result = query.all()
    model, size = seeds

    assert len(facets_results) == len(facets_list)

    facets = f.facets.values()

    for facet in facets:
        assert sum([bucket["count"] for bucket in facets_results[facet.name]["buckets"]]) == len(result) <= size

        for bucket in facets_results[facet.name]["buckets"]:
            result_count = len(list(filter(
                lambda inst: getattr(inst, facet.column_name) == bucket["value"],
                result
            )))
            assert result_count == bucket["count"]


@pytest.mark.parametrize("facets_list", FACETS)
@pytest.mark.parametrize("query", QUERIES)
@pytest.mark.parametrize("seeds", SEEDS, indirect=True)
def test_declare_filter(seeds, query, facets_list):

    f = declare_facets(facets_list)

    facets_results = f.get_facets(query)

    for name, facet_result in facets_results.items():
        for bucket in facet_result["buckets"]:
            new_filter = {name: {"values": [bucket["value"]]}}
            filtered_query = f.apply_filters(query, new_filter)
            assert len(filtered_query.all()) == bucket["count"]
