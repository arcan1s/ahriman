from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.build_tools.package_version import PackageVersion
from ahriman.core.configuration import Configuration
from ahriman.core.utils import utcnow
from ahriman.models.package import Package
from ahriman.models.pkgbuild import Pkgbuild


def test_actual_version(package_ahriman: Package, configuration: Configuration) -> None:
    """
    must return same actual_version as version is
    """
    assert PackageVersion(package_ahriman).actual_version(configuration) == package_ahriman.version


def test_actual_version_vcs(package_tpacpi_bat_git: Package, configuration: Configuration,
                            mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must return valid actual_version for VCS package
    """
    pkgbuild = resource_path_root / "models" / "package_tpacpi-bat-git_pkgbuild"
    mocker.patch("ahriman.models.pkgbuild.Pkgbuild.from_file", return_value=Pkgbuild.from_file(pkgbuild))
    mocker.patch("pathlib.Path.glob", return_value=[Path("local")])
    init_mock = mocker.patch("ahriman.core.build_tools.task.Task.init")
    unlink_mock = mocker.patch("pathlib.Path.unlink")

    assert PackageVersion(package_tpacpi_bat_git).actual_version(configuration) == "3.1.r13.g4959b52-1"
    init_mock.assert_called_once_with(configuration.repository_paths.cache_for(package_tpacpi_bat_git.base), [], None)
    unlink_mock.assert_called_once_with()


def test_actual_version_failed(package_tpacpi_bat_git: Package, configuration: Configuration,
                               mocker: MockerFixture) -> None:
    """
    must return same version in case if exception occurred
    """
    mocker.patch("ahriman.core.build_tools.task.Task.init", side_effect=Exception)
    mocker.patch("pathlib.Path.glob", return_value=[Path("local")])
    unlink_mock = mocker.patch("pathlib.Path.unlink")

    assert PackageVersion(package_tpacpi_bat_git).actual_version(configuration) == package_tpacpi_bat_git.version
    unlink_mock.assert_called_once_with()


def test_is_newer_than(package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must correctly check if package is newer than specified timestamp
    """
    # base checks, true/false
    older = package_ahriman.packages[package_ahriman.base].build_date - 1
    assert PackageVersion(package_ahriman).is_newer_than(older)

    newer = package_ahriman.packages[package_ahriman.base].build_date + 1
    assert not PackageVersion(package_ahriman).is_newer_than(newer)

    # list check
    min_date = min(package.build_date for package in package_python_schedule.packages.values())
    assert PackageVersion(package_python_schedule).is_newer_than(min_date)

    # null list check
    package_python_schedule.packages["python-schedule"].build_date = None
    assert PackageVersion(package_python_schedule).is_newer_than(min_date)

    package_python_schedule.packages["python2-schedule"].build_date = None
    assert not PackageVersion(package_python_schedule).is_newer_than(min_date)


def test_is_outdated_false(package_ahriman: Package, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must be not outdated for the same package
    """
    actual_version_mock = mocker.patch("ahriman.core.build_tools.package_version.PackageVersion.actual_version",
                                       return_value=package_ahriman.version)
    assert not PackageVersion(package_ahriman).is_outdated(package_ahriman, configuration)
    actual_version_mock.assert_called_once_with(configuration)


def test_is_outdated_true(package_ahriman: Package, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must be outdated for the new version
    """
    other = Package.from_json(package_ahriman.view())
    other.version = other.version.replace("-1", "-2")
    actual_version_mock = mocker.patch("ahriman.core.build_tools.package_version.PackageVersion.actual_version",
                                       return_value=other.version)

    assert PackageVersion(package_ahriman).is_outdated(other, configuration)
    actual_version_mock.assert_called_once_with(configuration)


def test_is_outdated_no_version_calculation(package_ahriman: Package, configuration: Configuration,
                                            mocker: MockerFixture) -> None:
    """
    must not call actual version if calculation is disabled
    """
    actual_version_mock = mocker.patch("ahriman.core.build_tools.package_version.PackageVersion.actual_version")
    assert not PackageVersion(package_ahriman).is_outdated(package_ahriman, configuration, calculate_version=False)
    actual_version_mock.assert_not_called()


def test_is_outdated_fresh_package(package_ahriman: Package, configuration: Configuration,
                                   mocker: MockerFixture) -> None:
    """
    must not call actual version if package is never than specified time
    """
    configuration.set_option("build", "vcs_allowed_age", str(int(utcnow().timestamp())))
    actual_version_mock = mocker.patch("ahriman.core.build_tools.package_version.PackageVersion.actual_version")
    assert not PackageVersion(package_ahriman).is_outdated(package_ahriman, configuration)
    actual_version_mock.assert_not_called()
