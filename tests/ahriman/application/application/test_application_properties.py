from ahriman.application.application.properties import Properties


def test_create_tree(application_properties: Properties) -> None:
    """
    must have repository attribute
    """
    assert application_properties.repository
