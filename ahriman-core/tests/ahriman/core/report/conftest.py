import pytest

from ahriman.core.configuration import Configuration
from ahriman.core.report.email import Email
from ahriman.core.report.remote_call import RemoteCall
from ahriman.core.report.rss import RSS
from ahriman.core.report.telegram import Telegram


@pytest.fixture
def email(configuration: Configuration) -> Email:
    """
    fixture for email trigger

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        Email: email trigger test instance
    """
    _, repository_id = configuration.check_loaded()
    return Email(repository_id, configuration, "email")


@pytest.fixture
def remote_call(configuration: Configuration) -> RemoteCall:
    """
    fixture for remote update trigger

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        RemoteCall: remote update trigger test instance
    """
    configuration.set_option("web", "host", "localhost")
    configuration.set_option("web", "port", "8080")
    _, repository_id = configuration.check_loaded()
    return RemoteCall(repository_id, configuration, "remote-call")


@pytest.fixture
def rss(configuration: Configuration) -> RSS:
    """
    fixture for rss trigger

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        RSS: rss trigger test instance
    """
    _, repository_id = configuration.check_loaded()
    return RSS(repository_id, configuration, "rss")


@pytest.fixture
def telegram(configuration: Configuration) -> Telegram:
    """
    fixture for telegram trigger

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        Telegram: telegram trigger test instance
    """
    _, repository_id = configuration.check_loaded()
    return Telegram(repository_id, configuration, "telegram")
