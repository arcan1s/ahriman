from ahriman.application.application.application_properties import ApplicationProperties


def test_create_tree(application_properties: ApplicationProperties) -> None:
    """
    must have repository attribute
    """
    assert application_properties.repository
