import pytest

from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.repository.cleaner import Cleaner
from ahriman.core.repository.executor import Executor
from ahriman.core.repository.properties import Properties
from ahriman.core.repository.repository import Repository
from ahriman.core.repository.update_handler import UpdateHandler


@pytest.fixture
def cleaner(configuration: Configuration, mocker: MockerFixture) -> Cleaner:
    mocker.patch("pathlib.Path.mkdir")
    return Cleaner("x86_64", configuration)


@pytest.fixture
def executor(configuration: Configuration, mocker: MockerFixture) -> Executor:
    mocker.patch("pathlib.Path.mkdir")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_build")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_cache")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_chroot")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_manual")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_packages")
    return Executor("x86_64", configuration)


@pytest.fixture
def repository(configuration: Configuration, mocker: MockerFixture) -> Repository:
    mocker.patch("pathlib.Path.mkdir")
    return Repository("x86_64", configuration)


@pytest.fixture
def properties(configuration: Configuration) -> Properties:
    return Properties("x86_64", configuration)


@pytest.fixture
def update_handler(configuration: Configuration, mocker: MockerFixture) -> UpdateHandler:
    mocker.patch("pathlib.Path.mkdir")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_build")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_cache")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_chroot")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_manual")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_packages")
    return UpdateHandler("x86_64", configuration)
