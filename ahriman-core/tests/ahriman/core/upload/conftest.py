import pytest

from typing import Any
from unittest.mock import MagicMock

from ahriman.core.configuration import Configuration
from ahriman.core.upload.github import GitHub
from ahriman.core.upload.remote_service import RemoteService
from ahriman.core.upload.rsync import Rsync
from ahriman.core.upload.s3 import S3


@pytest.fixture
def github(configuration: Configuration) -> GitHub:
    """
    fixture for GitHub synchronization

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        GitHub: GitHub test instance
    """
    _, repository_id = configuration.check_loaded()
    return GitHub(repository_id, configuration, "github:x86_64")


@pytest.fixture
def github_release() -> dict[str, Any]:
    """
    fixture for the GitHub release object

    Returns:
        dict[str, Any]: GitHub test release object
    """
    return {
        "url": "release_url",
        "assets_url": "assets_url",
        "upload_url": "upload_url{?name,label}",
        "tag_name": "x86_64",
        "name": "x86_64",
        "assets": [{
            "url": "asset_url",
            "name": "asset_name",
        }],
        "body": None,
    }


@pytest.fixture
def remote_service(configuration: Configuration) -> RemoteService:
    """
    fixture for remote service synchronization

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        RemoteService: remote service test instance
    """
    configuration.set_option("web", "host", "localhost")
    configuration.set_option("web", "port", "8080")
    _, repository_id = configuration.check_loaded()
    return RemoteService(repository_id, configuration, "remote-service")


@pytest.fixture
def rsync(configuration: Configuration) -> Rsync:
    """
    fixture for rsync synchronization

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        Rsync: rsync test instance
    """
    _, repository_id = configuration.check_loaded()
    return Rsync(repository_id, configuration, "rsync")


@pytest.fixture
def s3(configuration: Configuration) -> S3:
    """
    fixture for S3 synchronization

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        S3: S3 test instance
    """
    _, repository_id = configuration.check_loaded()
    return S3(repository_id, configuration, "customs3")


@pytest.fixture
def s3_remote_objects(configuration: Configuration) -> list[MagicMock]:
    """
    fixture for boto3 like S3 objects

    Returns:
        list[MagicMock]: boto3 like S3 objects test instance
    """
    _, repository_id = configuration.check_loaded()
    delete_mock = MagicMock()

    result = []
    for item in ["a", "b", "c"]:
        s3_object = MagicMock()
        s3_object.key = f"{repository_id.name}/{repository_id.architecture}/{item}"
        s3_object.e_tag = f"\"{item}\""
        s3_object.delete = delete_mock

        result.append(s3_object)

    return result
