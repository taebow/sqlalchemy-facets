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
        assert isinstance(class_._root_facets, dict)
        assert len(class_._root_facets) == 1
        assert name in class_._root_facets
        assert isinstance(class_._root_facets[name], FacetMock)
        assert class_._root_facets[name].name == name

    test_facet_setup(TestFacetedQuery, "some_attr")
    test_facet_setup(TestFacetedQuery2, "another")


def test_default_column_name():

    class FacetMock(Facet):
        pass

    class TestFacetedQuery(FacetedQuery):
        some_attr = FacetMock()

    assert TestFacetedQuery._root_facets["some_attr"].column_name == "some_attr"


def test_column_name_override():

    class FacetMock(Facet):
        pass

    class TestFacetedQuery(FacetedQuery):
        some_attr = FacetMock("another")

    assert TestFacetedQuery._root_facets["some_attr"].column_name == "another"


def test_sub_facets_init():

    class FacetMock1(Facet):
        pass

    class FacetMock2(Facet):
        pass


    class TestFacetedQuery(FacetedQuery):

        root_attr1 = FacetMock1(
            sub_attr = FacetMock2()
        )

        root_attr2 = FacetMock1(
            sub_attr = FacetMock2()
        )

    print(TestFacetedQuery._column_facets)
    for f in TestFacetedQuery._column_facets:
        print(f.name)
    assert len(TestFacetedQuery._column_facets) == 3
