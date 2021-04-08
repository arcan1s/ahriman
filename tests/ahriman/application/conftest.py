import argparse
import aur
import pytest

from pytest_mock import MockerFixture

from ahriman.application.ahriman import _parser
from ahriman.application.application import Application
from ahriman.application.lock import Lock
from ahriman.core.configuration import Configuration
from ahriman.models.package import Package


@pytest.fixture
def application(configuration: Configuration, mocker: MockerFixture) -> Application:
    mocker.patch("pathlib.Path.mkdir")
    return Application("x86_64", configuration)


@pytest.fixture
def args() -> argparse.Namespace:
    return argparse.Namespace(lock=None, force=False, unsafe=False, no_report=True)


@pytest.fixture
def aur_package_ahriman(package_ahriman: Package) -> aur.Package:
    return aur.Package(
        num_votes=None,
        description=package_ahriman.packages[package_ahriman.base].description,
        url_path=package_ahriman.web_url,
        last_modified=None,
        name=package_ahriman.base,
        out_of_date=None,
        id=None,
        first_submitted=None,
        maintainer=None,
        version=package_ahriman.version,
        license=package_ahriman.packages[package_ahriman.base].licenses,
        url=None,
        package_base=package_ahriman.base,
        package_base_id=None,
        category_id=None)


@pytest.fixture
def lock(args: argparse.Namespace, configuration: Configuration) -> Lock:
    return Lock(args, "x86_64", configuration)


@pytest.fixture
def parser() -> argparse.ArgumentParser:
    return _parser()
