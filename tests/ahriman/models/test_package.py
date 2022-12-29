import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.exceptions import PackageInfoError
from ahriman.models.aur_package import AURPackage
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


def test_depends(package_python_schedule: Package) -> None:
    """
    must return combined list of dependencies
    """
    assert all(
        set(package_python_schedule.depends).intersection(package.depends)
        for package in package_python_schedule.packages.values()
    )


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


def test_from_archive(package_ahriman: Package, pyalpm_handle: MagicMock, mocker: MockerFixture) -> None:
    """
    must construct package from alpm library
    """
    mocker.patch("ahriman.models.package_description.PackageDescription.from_package",
                 return_value=package_ahriman.packages[package_ahriman.base])
    assert Package.from_archive(Path("path"), pyalpm_handle, package_ahriman.remote) == package_ahriman


def test_from_aur(package_ahriman: Package, aur_package_ahriman: AURPackage, pacman: Pacman,
                  mocker: MockerFixture) -> None:
    """
    must construct package from aur
    """
    mocker.patch("ahriman.core.alpm.remote.AUR.info", return_value=aur_package_ahriman)

    package = Package.from_aur(package_ahriman.base, pacman)
    assert package_ahriman.base == package.base
    assert package_ahriman.version == package.version
    assert package_ahriman.packages.keys() == package.packages.keys()


def test_from_build(package_ahriman: Package, mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must construct package from srcinfo
    """
    srcinfo = (resource_path_root / "models" / "package_ahriman_srcinfo").read_text()
    mocker.patch("ahriman.models.package.Package._check_output", return_value=srcinfo)

    package = Package.from_build(Path("path"))
    assert package_ahriman.packages.keys() == package.packages.keys()
    package_ahriman.packages = package.packages  # we are not going to test PackageDescription here
    package_ahriman.remote = None
    assert package_ahriman == package


def test_from_build_failed(package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must raise exception if there are errors during srcinfo load
    """
    mocker.patch("ahriman.models.package.Package._check_output", return_value="")
    mocker.patch("ahriman.models.package.parse_srcinfo", return_value=({"packages": {}}, ["an error"]))

    with pytest.raises(PackageInfoError):
        Package.from_build(Path("path"))


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


def test_from_official(package_ahriman: Package, aur_package_ahriman: AURPackage, pacman: Pacman,
                       mocker: MockerFixture) -> None:
    """
    must construct package from official repository
    """
    mocker.patch("ahriman.core.alpm.remote.Official.info", return_value=aur_package_ahriman)

    package = Package.from_official(package_ahriman.base, pacman)
    assert package_ahriman.base == package.base
    assert package_ahriman.version == package.version
    assert package_ahriman.packages.keys() == package.packages.keys()


def test_dependencies_failed(mocker: MockerFixture) -> None:
    """
    must raise exception if there are errors during srcinfo load for dependencies
    """
    mocker.patch("ahriman.models.package.Package._check_output", return_value="")
    mocker.patch("ahriman.models.package.parse_srcinfo", return_value=({"packages": {}}, ["an error"]))

    with pytest.raises(PackageInfoError):
        Package.dependencies(Path("path"))


def test_dependencies_with_version(mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must load correct list of dependencies with version
    """
    srcinfo = (resource_path_root / "models" / "package_yay_srcinfo").read_text()
    mocker.patch("ahriman.models.package.Package._check_output", return_value=srcinfo)

    assert Package.dependencies(Path("path")) == {"git", "go", "pacman"}


def test_dependencies_with_version_and_overlap(mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must load correct list of dependencies with version
    """
    srcinfo = (resource_path_root / "models" / "package_gcc10_srcinfo").read_text()
    mocker.patch("ahriman.models.package.Package._check_output", return_value=srcinfo)

    assert Package.dependencies(Path("path")) == {"glibc", "doxygen", "binutils", "git", "libmpc", "python", "zstd"}


def test_supported_architectures(mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must generate list of available architectures
    """
    srcinfo = (resource_path_root / "models" / "package_yay_srcinfo").read_text()
    mocker.patch("ahriman.models.package.Package._check_output", return_value=srcinfo)
    assert Package.supported_architectures(Path("path")) == \
        {"i686", "pentium4", "x86_64", "arm", "armv7h", "armv6h", "aarch64"}


def test_supported_architectures_failed(mocker: MockerFixture) -> None:
    """
    must raise exception if there are errors during srcinfo load for architectures
    """
    mocker.patch("ahriman.models.package.Package._check_output", return_value="")
    mocker.patch("ahriman.models.package.parse_srcinfo", return_value=({"packages": {}}, ["an error"]))

    with pytest.raises(PackageInfoError):
        Package.supported_architectures(Path("path"))


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
    must return same version in case if there are errors during parse
    """
    mocker.patch("pathlib.Path.read_text", return_value="")
    mocker.patch("ahriman.models.package.parse_srcinfo", return_value=({"packages": {}}, ["an error"]))
    mocker.patch("ahriman.models.package.Package._check_output")
    mocker.patch("ahriman.core.build_tools.sources.Sources.load")

    assert package_tpacpi_bat_git.actual_version(repository_paths) == package_tpacpi_bat_git.version


def test_full_depends(package_ahriman: Package, package_python_schedule: Package, pyalpm_package_ahriman: MagicMock,
                      pyalpm_handle: MagicMock) -> None:
    """
    must extract all dependencies from the package
    """
    package_python_schedule.packages[package_python_schedule.base].provides = ["python3-schedule"]

    database_mock = MagicMock()
    database_mock.pkgcache = [pyalpm_package_ahriman]
    pyalpm_handle.handle.get_syncdbs.return_value = [database_mock]

    assert package_ahriman.full_depends(pyalpm_handle, [package_python_schedule]) == package_ahriman.depends

    package_python_schedule.packages[package_python_schedule.base].depends = [package_ahriman.base]
    expected = sorted(set(package_python_schedule.depends + package_ahriman.depends))
    assert package_python_schedule.full_depends(pyalpm_handle, [package_python_schedule]) == expected


def test_is_newer_than(package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must correctly check if package is newer than specified timestamp
    """
    # base checks, true/false
    assert package_ahriman.is_newer_than(package_ahriman.packages[package_ahriman.base].build_date - 1)
    assert not package_ahriman.is_newer_than(package_ahriman.packages[package_ahriman.base].build_date + 1)

    # list check
    min_date = min(package.build_date for package in package_python_schedule.packages.values())
    assert package_python_schedule.is_newer_than(min_date)

    # null list check
    package_python_schedule.packages["python-schedule"].build_date = None
    assert package_python_schedule.is_newer_than(min_date)

    package_python_schedule.packages["python2-schedule"].build_date = None
    assert not package_python_schedule.is_newer_than(min_date)


def test_is_outdated_false(package_ahriman: Package, repository_paths: RepositoryPaths) -> None:
    """
    must be not outdated for the same package
    """
    assert not package_ahriman.is_outdated(package_ahriman, repository_paths, calculate_version=True)


def test_is_outdated_true(package_ahriman: Package, repository_paths: RepositoryPaths) -> None:
    """
    must be outdated for the new version
    """
    other = Package.from_json(package_ahriman.view())
    other.version = other.version.replace("-1", "-2")

    assert package_ahriman.is_outdated(other, repository_paths, calculate_version=True)


def test_build_status_pretty_print(package_ahriman: Package) -> None:
    """
    must return string in pretty print function
    """
    assert package_ahriman.pretty_print()
    assert isinstance(package_ahriman.pretty_print(), str)
