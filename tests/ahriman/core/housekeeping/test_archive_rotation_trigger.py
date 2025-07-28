import pytest

from dataclasses import replace
from pathlib import Path
from pytest_mock import MockerFixture
from typing import Any
from unittest.mock import call as MockCall

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.configuration import Configuration
from ahriman.core.housekeeping import ArchiveRotationTrigger
from ahriman.models.package import Package
from ahriman.models.result import Result


def test_configuration_sections(configuration: Configuration) -> None:
    """
    must correctly parse target list
    """
    assert ArchiveRotationTrigger.configuration_sections(configuration) == ["archive"]


def test_archives_remove(archive_rotation_trigger: ArchiveRotationTrigger, package_ahriman: Package,
                         pacman: Pacman, mocker: MockerFixture) -> None:
    """
    must remove older packages
    """
    def package(version: Any, *args: Any, **kwargs: Any) -> Package:
        generated = replace(package_ahriman, version=str(version))
        generated.packages = {
            key: replace(value, filename=str(version))
            for key, value in generated.packages.items()
        }
        return generated

    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("ahriman.core.housekeeping.archive_rotation_trigger.package_like", return_value=True)
    mocker.patch("pathlib.Path.glob", return_value=[Path(str(i)) for i in range(5)])
    mocker.patch("pathlib.Path.iterdir", return_value=[Path(str(i)) for i in range(5)])
    mocker.patch("ahriman.models.package.Package.from_archive", side_effect=package)
    unlink_mock = mocker.patch("pathlib.Path.unlink", autospec=True)

    archive_rotation_trigger.archives_remove(package_ahriman, pacman)
    unlink_mock.assert_has_calls([
        MockCall(Path("0")),
        MockCall(Path("1")),
    ])


def test_archives_remove_keep(archive_rotation_trigger: ArchiveRotationTrigger, package_ahriman: Package,
                              pacman: Pacman, mocker: MockerFixture) -> None:
    """
    must keep all packages if set to
    """
    def package(version: Any, *args: Any, **kwargs: Any) -> Package:
        generated = replace(package_ahriman, version=str(version))
        generated.packages = {
            key: replace(value, filename=str(version))
            for key, value in generated.packages.items()
        }
        return generated

    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("ahriman.core.housekeeping.archive_rotation_trigger.package_like", return_value=True)
    mocker.patch("pathlib.Path.glob", return_value=[Path(str(i)) for i in range(5)])
    mocker.patch("pathlib.Path.iterdir", return_value=[Path(str(i)) for i in range(5)])
    mocker.patch("ahriman.models.package.Package.from_archive", side_effect=package)
    unlink_mock = mocker.patch("pathlib.Path.unlink", autospec=True)

    archive_rotation_trigger.keep_built_packages = 0
    archive_rotation_trigger.archives_remove(package_ahriman, pacman)
    unlink_mock.assert_not_called()


def test_on_result(archive_rotation_trigger: ArchiveRotationTrigger, package_ahriman: Package,
                   package_python_schedule: Package, mocker: MockerFixture) -> None:
    """
    must rotate archives
    """
    mocker.patch("ahriman.core._Context.get")
    remove_mock = mocker.patch("ahriman.core.housekeeping.ArchiveRotationTrigger.archives_remove")
    archive_rotation_trigger.on_result(Result(added=[package_ahriman], failed=[package_python_schedule]), [])
    remove_mock.assert_called_once_with(package_ahriman, pytest.helpers.anyvar(int))
