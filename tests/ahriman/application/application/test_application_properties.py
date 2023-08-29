from ahriman.application.application.application_properties import ApplicationProperties


def test_create_tree(application_properties: ApplicationProperties) -> None:
    """
    must have repository attribute
    """
    assert application_properties.repository


def test_architecture(application_properties: ApplicationProperties) -> None:
    """
    must return repository architecture
    """
    assert application_properties.architecture == application_properties.repository_id.architecture
