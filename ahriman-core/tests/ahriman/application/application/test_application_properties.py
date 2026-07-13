from ahriman.application.application.application_properties import ApplicationProperties


def test_architecture(application_properties: ApplicationProperties) -> None:
    """
    must return repository architecture
    """
    assert application_properties.architecture == application_properties.repository_id.architecture


def test_reporter(application_properties: ApplicationProperties) -> None:
    """
    must have reporter attribute
    """
    assert application_properties.reporter
