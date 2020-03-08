from sqlalchemy_facets import FacetedQuery
from sqlalchemy_facets import Facet

def test_facets_declaration_setup():

    class FacetMock(Facet):
        pass

    class TestFacetedQuery(FacetedQuery):
        some_attr = FacetMock()
        not_included = dict()

    class TestFacetedQuery2(FacetedQuery):
        another = FacetMock()

    def test_facet_setup(class_, name):
        assert isinstance(class_.facets, dict)
        assert len(class_.facets) == 1
        assert name in class_.facets
        assert isinstance(class_.facets[name], FacetMock)
        assert class_.facets[name].name == name

    test_facet_setup(TestFacetedQuery, "some_attr")
    test_facet_setup(TestFacetedQuery2, "another")


def test_default_column_name():

    class FacetMock(Facet):
        pass

    class TestFacetedQuery(FacetedQuery):
        some_attr = FacetMock()

    assert TestFacetedQuery.facets["some_attr"].column_name == "some_attr"