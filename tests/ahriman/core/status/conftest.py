import pytest

from typing import Any, Dict

from ahriman.core.status.client import Client
from ahriman.core.status.web_client import WebClient
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.package import Package


# helpers
@pytest.helpers.register
def get_package_status(package: Package) -> Dict[str, Any]:
    return {"status": BuildStatusEnum.Unknown.value, "package": package.view()}


@pytest.helpers.register
def get_package_status_extended(package: Package) -> Dict[str, Any]:
    return {"status": BuildStatus().view(), "package": package.view()}


# fixtures
@pytest.fixture
def client() -> Client:
    return Client()


@pytest.fixture
def web_client() -> WebClient:
    return WebClient("localhost", 8080)
