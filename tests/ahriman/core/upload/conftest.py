import pytest

from collections import namedtuple
from typing import Any, Dict, List
from unittest.mock import MagicMock

from ahriman.core.configuration import Configuration
from ahriman.core.upload.github import Github
from ahriman.core.upload.rsync import Rsync
from ahriman.core.upload.s3 import S3


_s3_object = namedtuple("s3_object", ["key", "e_tag", "delete"])


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
def github_release() -> Dict[str, Any]:
    """
    fixture for the github release object

    Returns:
      Dict[str, Any]: github test release object
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
def s3_remote_objects() -> List[_s3_object]:
    """
    fixture for boto3 like S3 objects

    Returns:
      List[_s3_object]: boto3 like S3 objects test instance
    """
    delete_mock = MagicMock()
    return list(map(lambda item: _s3_object(f"x86_64/{item}", f"\"{item}\"", delete_mock), ["a", "b", "c"]))
