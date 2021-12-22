import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import MagicMock, PropertyMock

from ahriman.core.exceptions import InvalidPackageInfo
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource
from ahriman.models.repository_paths import RepositoryPaths


def test_depends(package_python_schedule: Package) -> None:
    """
    must return combined list of dependencies
    """
    assert all(
        set(package_python_schedule.depends).intersection(package.depends)
        for package in package_python_schedule.packages.values()
    )


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


def test_from_build_failed(package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must raise exception if there are errors during srcinfo load
    """
    mocker.patch("pathlib.Path.read_text", return_value="")
    mocker.patch("ahriman.models.package.parse_srcinfo", return_value=({"packages": {}}, ["an error"]))

    with pytest.raises(InvalidPackageInfo):
        Package.from_build(Path("path"), package_ahriman.aur_url)


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


def test_load_resolve(package_ahriman: Package, pyalpm_handle: MagicMock, mocker: MockerFixture) -> None:
    """
    must resolve source before package loading
    """
    resolve_mock = mocker.patch("ahriman.models.package_source.PackageSource.resolve",
                                return_value=PackageSource.Archive)
    mocker.patch("ahriman.models.package.Package.from_archive")

    Package.load("path", PackageSource.Archive, pyalpm_handle, package_ahriman.aur_url)
    resolve_mock.assert_called_once_with("path")


def test_load_from_archive(package_ahriman: Package, pyalpm_handle: MagicMock, mocker: MockerFixture) -> None:
    """
    must load package from package archive
    """
    load_mock = mocker.patch("ahriman.models.package.Package.from_archive")
    Package.load("path", PackageSource.Archive, pyalpm_handle, package_ahriman.aur_url)
    load_mock.assert_called_once()


def test_load_from_aur(package_ahriman: Package, pyalpm_handle: MagicMock, mocker: MockerFixture) -> None:
    """
    must load package from AUR
    """
    load_mock = mocker.patch("ahriman.models.package.Package.from_aur")
    Package.load("path", PackageSource.AUR, pyalpm_handle, package_ahriman.aur_url)
    load_mock.assert_called_once()


def test_load_from_build(package_ahriman: Package, pyalpm_handle: MagicMock, mocker: MockerFixture) -> None:
    """
    must load package from build directory
    """
    load_mock = mocker.patch("ahriman.models.package.Package.from_build")
    Package.load("path", PackageSource.Local, pyalpm_handle, package_ahriman.aur_url)
    load_mock.assert_called_once()


def test_load_failure(package_ahriman: Package, pyalpm_handle: MagicMock, mocker: MockerFixture) -> None:
    """
    must raise InvalidPackageInfo on exception
    """
    mocker.patch("ahriman.models.package.Package.from_aur", side_effect=InvalidPackageInfo("exception!"))
    with pytest.raises(InvalidPackageInfo):
        Package.load("path", PackageSource.AUR, pyalpm_handle, package_ahriman.aur_url)


def test_load_failure_exception(package_ahriman: Package, pyalpm_handle: MagicMock, mocker: MockerFixture) -> None:
    """
    must raise InvalidPackageInfo on random eexception
    """
    mocker.patch("ahriman.models.package.Package.from_aur", side_effect=Exception())
    with pytest.raises(InvalidPackageInfo):
        Package.load("path", PackageSource.AUR, pyalpm_handle, package_ahriman.aur_url)


def test_load_invalid_source(package_ahriman: Package, pyalpm_handle: MagicMock) -> None:
    """
    must raise InvalidPackageInfo on unsupported source
    """
    with pytest.raises(InvalidPackageInfo):
        Package.load("path", PackageSource.Remote, pyalpm_handle, package_ahriman.aur_url)


def test_dependencies_failed(mocker: MockerFixture) -> None:
    """
    must raise exception if there are errors during srcinfo load
    """
    mocker.patch("pathlib.Path.read_text", return_value="")
    mocker.patch("ahriman.models.package.parse_srcinfo", return_value=({"packages": {}}, ["an error"]))

    with pytest.raises(InvalidPackageInfo):
        Package.dependencies(Path("path"))


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
    mocker.patch("ahriman.core.build_tools.sources.Sources.load")

    assert package_tpacpi_bat_git.actual_version(repository_paths) == "3.1.r13.g4959b52-1"


def test_actual_version_srcinfo_failed(package_tpacpi_bat_git: Package, repository_paths: RepositoryPaths,
                                       mocker: MockerFixture) -> None:
    """
    must return same version in case if exception occurred
    """
    mocker.patch("ahriman.models.package.Package._check_output", side_effect=Exception())
    mocker.patch("ahriman.core.build_tools.sources.Sources.load")

    assert package_tpacpi_bat_git.actual_version(repository_paths) == package_tpacpi_bat_git.version


def test_actual_version_vcs_failed(package_tpacpi_bat_git: Package, repository_paths: RepositoryPaths,
                                   mocker: MockerFixture) -> None:
    """
    must return same version in case if exception occurred
    """
    mocker.patch("pathlib.Path.read_text", return_value="")
    mocker.patch("ahriman.models.package.parse_srcinfo", return_value=({"packages": {}}, ["an error"]))
    mocker.patch("ahriman.models.package.Package._check_output")
    mocker.patch("ahriman.core.build_tools.sources.Sources.load")

    assert package_tpacpi_bat_git.actual_version(repository_paths) == package_tpacpi_bat_git.version


def test_full_depends(package_ahriman: Package, package_python_schedule: Package, pyalpm_package_ahriman: MagicMock,
                      pyalpm_handle: MagicMock, mocker: MockerFixture) -> None:
    """
    must extract all dependencies from the package
    """
    package_python_schedule.packages[package_python_schedule.base].provides = ["python3-schedule"]

    database_mock = MagicMock()
    database_mock.pkgcache = [pyalpm_package_ahriman]
    pyalpm_handle.handle.get_syncdbs.return_value = [database_mock]

    assert package_ahriman.full_depends(pyalpm_handle, [package_python_schedule]) == package_ahriman.depends

    package_python_schedule.packages[package_python_schedule.base].depends = [package_ahriman.base]
    expected = sorted(set(package_python_schedule.depends + ["python-aur"]))
    assert package_python_schedule.full_depends(pyalpm_handle, [package_python_schedule]) == expected


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


def test_build_status_pretty_print(package_ahriman: Package) -> None:
    """
    must return string in pretty print function
    """
    assert package_ahriman.pretty_print()
    assert isinstance(package_ahriman.pretty_print(), str)
