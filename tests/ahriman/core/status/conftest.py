import pytest

from typing import Any, Dict

from ahriman.core.status.client import Client
from ahriman.core.status.web_client import WebClient
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.package import Package


# helpers
@pytest.helpers.register
def get_package_status(package: Package) -> Dict[str, Any]:
    """
    helper to extract package status from package
    :param package: package object
    :return: simplified package status map (with only status and view)
    """
    return {"status": BuildStatusEnum.Unknown.value, "package": package.view()}


@pytest.helpers.register
def get_package_status_extended(package: Package) -> Dict[str, Any]:
    """
    helper to extract package status from package
    :param package: package object
    :return: full package status map (with timestamped build status and view)
    """
    return {"status": BuildStatus().view(), "package": package.view()}


# fixtures
@pytest.fixture
def client() -> Client:
    """
    fixture for dummy client
    :return: dummy client test instance
    """
    return Client()


@pytest.fixture
def web_client() -> WebClient:
    """
    fixture for web client
    :return: web client test instance
    """
    return WebClient("localhost", 8080)
