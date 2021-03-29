import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import MagicMock, PropertyMock

from ahriman.core.exceptions import InvalidPackageInfo
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


def test_git_url(package_ahriman: Package) -> None:
    """
    must generate valid git url
    """
    assert package_ahriman.git_url.endswith(".git")
    assert package_ahriman.git_url.startswith(package_ahriman.aur_url)
    assert package_ahriman.base in package_ahriman.git_url


def test_groups(package_ahriman: Package) -> None:
    """
    must return list of groups for each package
    """
    assert all(
        all(group in package_ahriman.groups for group in package.groups)
        for package in package_ahriman.packages.values()
    )
    assert sorted(package_ahriman.groups) == package_ahriman.groups


def test_is_single_package_false(package_python_schedule: Package) -> None:
    """
    python-schedule must not be single package
    """
    assert not package_python_schedule.is_single_package


def test_is_single_package_true(package_ahriman: Package) -> None:
    """
    ahriman must be single package
    """
    assert package_ahriman.is_single_package


def test_is_vcs_false(package_ahriman: Package) -> None:
    """
    ahriman must not be VCS package
    """
    assert not package_ahriman.is_vcs


def test_is_vcs_true(package_tpacpi_bat_git: Package) -> None:
    """
    tpacpi-bat-git must be VCS package
    """
    assert package_tpacpi_bat_git.is_vcs


def test_licenses(package_ahriman: Package) -> None:
    """
    must return list of licenses for each package
    """
    assert all(
        all(lic in package_ahriman.licenses for lic in package.licenses)
        for package in package_ahriman.packages.values()
    )
    assert sorted(package_ahriman.licenses) == package_ahriman.licenses


def test_web_url(package_ahriman: Package) -> None:
    """
    must generate valid web url
    """
    assert package_ahriman.web_url.startswith(package_ahriman.aur_url)
    assert package_ahriman.base in package_ahriman.web_url


def test_from_archive(package_ahriman: Package, pyalpm_handle: MagicMock, mocker: MockerFixture) -> None:
    """
    must construct package from alpm library
    """
    mocker.patch("ahriman.models.package_description.PackageDescription.from_package",
                 return_value=package_ahriman.packages[package_ahriman.base])
    assert Package.from_archive(Path("path"), pyalpm_handle, package_ahriman.aur_url) == package_ahriman


def test_from_aur(package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must construct package from aur
    """
    mock = MagicMock()
    type(mock).name = PropertyMock(return_value=package_ahriman.base)
    type(mock).package_base = PropertyMock(return_value=package_ahriman.base)
    type(mock).version = PropertyMock(return_value=package_ahriman.version)
    mocker.patch("aur.info", return_value=mock)

    package = Package.from_aur(package_ahriman.base, package_ahriman.aur_url)
    assert package_ahriman.base == package.base
    assert package_ahriman.version == package.version
    assert package_ahriman.packages.keys() == package.packages.keys()


def test_from_build(package_ahriman: Package, mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must construct package from srcinfo
    """
    srcinfo = (resource_path_root / "models" / "package_ahriman_srcinfo").read_text()
    mocker.patch("pathlib.Path.read_text", return_value=srcinfo)

    package = Package.from_build(Path("path"), package_ahriman.aur_url)
    assert package_ahriman.packages.keys() == package.packages.keys()
    package_ahriman.packages = package.packages  # we are not going to test PackageDescription here
    assert package_ahriman == package


def test_from_json_view_1(package_ahriman: Package) -> None:
    """
    must construct same object from json
    """
    assert Package.from_json(package_ahriman.view()) == package_ahriman


def test_from_json_view_2(package_python_schedule: Package) -> None:
    """
    must construct same object from json
    """
    assert Package.from_json(package_python_schedule.view()) == package_python_schedule


def test_from_json_view_3(package_tpacpi_bat_git: Package) -> None:
    """
    must construct same object from json
    """
    assert Package.from_json(package_tpacpi_bat_git.view()) == package_tpacpi_bat_git


def test_dependencies_with_version(mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must load correct list of dependencies with version
    """
    srcinfo = (resource_path_root / "models" / "package_yay_srcinfo").read_text()
    mocker.patch("pathlib.Path.read_text", return_value=srcinfo)

    assert Package.dependencies(Path("path")) == {"git", "go", "pacman"}


def test_full_version() -> None:
    """
    must construct full version
    """
    assert Package.full_version("1", "r2388.d30e3201", "1") == "1:r2388.d30e3201-1"
    assert Package.full_version(None, "0.12.1", "1") == "0.12.1-1"


def test_load_from_archive(package_ahriman: Package, pyalpm_handle: MagicMock, mocker: MockerFixture) -> None:
    """
    must load package from package archive
    """
    mocker.patch("pathlib.Path.is_file", return_value=True)
    load_mock = mocker.patch("ahriman.models.package.Package.from_archive")

    Package.load(Path("path"), pyalpm_handle, package_ahriman.aur_url)
    load_mock.assert_called_once()


def test_load_from_aur(package_ahriman: Package, pyalpm_handle: MagicMock, mocker: MockerFixture) -> None:
    """
    must load package from AUR
    """
    load_mock = mocker.patch("ahriman.models.package.Package.from_aur")

    Package.load(Path("path"), pyalpm_handle, package_ahriman.aur_url)
    load_mock.assert_called_once()


def test_load_from_build(package_ahriman: Package, pyalpm_handle: MagicMock, mocker: MockerFixture) -> None:
    """
    must load package from build directory
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    load_mock = mocker.patch("ahriman.models.package.Package.from_build")

    Package.load(Path("path"), pyalpm_handle, package_ahriman.aur_url)
    load_mock.assert_called_once()


def test_load_failure(package_ahriman: Package, pyalpm_handle: MagicMock, mocker: MockerFixture) -> None:
    """
    must raise InvalidPackageInfo on exception
    """
    mocker.patch("pathlib.Path.is_dir", side_effect=InvalidPackageInfo("exception!"))
    with pytest.raises(InvalidPackageInfo):
        Package.load(Path("path"), pyalpm_handle, package_ahriman.aur_url)

    mocker.patch("pathlib.Path.is_dir", side_effect=Exception())
    with pytest.raises(InvalidPackageInfo):
        Package.load(Path("path"), pyalpm_handle, package_ahriman.aur_url)


def test_actual_version(package_ahriman: Package, repository_paths: RepositoryPaths) -> None:
    """
    must return same actual_version as version is
    """
    assert package_ahriman.actual_version(repository_paths) == package_ahriman.version


def test_actual_version_vcs(package_tpacpi_bat_git: Package, repository_paths: RepositoryPaths,
                            mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must return valid actual_version for VCS package
    """
    srcinfo = (resource_path_root / "models" / "package_tpacpi-bat-git_srcinfo").read_text()
    mocker.patch("ahriman.models.package.Package._check_output", return_value=srcinfo)
    mocker.patch("ahriman.core.build_tools.task.Task.fetch")

    assert package_tpacpi_bat_git.actual_version(repository_paths) == "3.1.r13.g4959b52-1"


def test_actual_version_vcs_failed(package_tpacpi_bat_git: Package, repository_paths: RepositoryPaths,
                                   mocker: MockerFixture) -> None:
    """
    must return same version in case if exception occurred
    """
    mocker.patch("ahriman.models.package.Package._check_output", side_effect=Exception())
    mocker.patch("ahriman.core.build_tools.task.Task.fetch")

    assert package_tpacpi_bat_git.actual_version(repository_paths) == package_tpacpi_bat_git.version


def test_is_outdated_false(package_ahriman: Package, repository_paths: RepositoryPaths) -> None:
    """
    must be not outdated for the same package
    """
    assert not package_ahriman.is_outdated(package_ahriman, repository_paths)


def test_is_outdated_true(package_ahriman: Package, repository_paths: RepositoryPaths) -> None:
    """
    must be outdated for the new version
    """
    other = Package.from_json(package_ahriman.view())
    other.version = other.version.replace("-1", "-2")

    assert package_ahriman.is_outdated(other, repository_paths)
