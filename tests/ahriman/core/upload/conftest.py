import pytest

from collections import namedtuple
from typing import List
from unittest.mock import MagicMock

from ahriman.core.configuration import Configuration
from ahriman.core.upload.s3 import S3


_s3_object = namedtuple("s3_object", ["key", "e_tag", "delete"])


@pytest.fixture
def s3(configuration: Configuration) -> S3:
    """
    fixture for S3 synchronization
    :param configuration: configuration fixture
    :return: S3 test instance
    """
    return S3("x86_64", configuration)


@pytest.fixture
def s3_remote_objects() -> List[_s3_object]:
    """
    fixture for boto3 like S3 objects
    :return: boto3 like S3 objects test instance
    """
    delete_mock = MagicMock()
    return list(map(lambda item: _s3_object(f"x86_64/{item}", f"\"{item}\"", delete_mock), ["a", "b", "c"]))
