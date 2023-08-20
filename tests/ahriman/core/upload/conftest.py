import pytest

from typing import Any
from unittest.mock import MagicMock

from ahriman.core.configuration import Configuration
from ahriman.core.upload.github import Github
from ahriman.core.upload.remote_service import RemoteService
from ahriman.core.upload.rsync import Rsync
from ahriman.core.upload.s3 import S3


@pytest.fixture
def github(configuration: Configuration) -> Github:
    """
    fixture for github synchronization

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        Github: github test instance
    """
    return Github("x86_64", configuration, "github:x86_64")


@pytest.fixture
def github_release() -> dict[str, Any]:
    """
    fixture for the github release object

    Returns:
        dict[str, Any]: github test release object
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
    return RemoteService("x86_64", configuration, "remote-service")


@pytest.fixture
def rsync(configuration: Configuration) -> Rsync:
    """
    fixture for rsync synchronization

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        Rsync: rsync test instance
    """
    return Rsync("x86_64", configuration, "rsync")


@pytest.fixture
def s3(configuration: Configuration) -> S3:
    """
    fixture for S3 synchronization

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        S3: S3 test instance
    """
    return S3("x86_64", configuration, "customs3")


@pytest.fixture
def s3_remote_objects() -> list[MagicMock]:
    """
    fixture for boto3 like S3 objects

    Returns:
        list[MagicMock]: boto3 like S3 objects test instance
    """
    delete_mock = MagicMock()

    result = []
    for item in ["a", "b", "c"]:
        s3_object = MagicMock()
        s3_object.key = f"x86_64/{item}"
        s3_object.e_tag = f"\"{item}\""
        s3_object.delete = delete_mock

        result.append(s3_object)

    return result
