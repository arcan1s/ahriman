import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest import mock
from unittest.mock import MagicMock

from ahriman.application.application.packages import Packages
from ahriman.models.package import Package
from ahriman.models.package_description import PackageDescription
from ahriman.models.package_source import PackageSource


def test_finalize(application_packages: Packages) -> None:
    """
    must raise NotImplemented for missing finalize method
    """
    with pytest.raises(NotImplementedError):
        application_packages._finalize([])


def test_known_packages(application_packages: Packages) -> None:
    """
    must raise NotImplemented for missing finalize method
    """
    with pytest.raises(NotImplementedError):
        application_packages._known_packages()


def test_add_archive(application_packages: Packages, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must add package from archive
    """
    copy_mock = mocker.patch("shutil.copy")
    application_packages._add_archive(package_ahriman.base)
    copy_mock.assert_called_once()


def test_add_aur(application_packages: Packages, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must add package from AUR
    """
    mocker.patch("ahriman.models.package.Package.load", return_value=package_ahriman)
    load_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.load")
    dependencies_mock = mocker.patch("ahriman.application.application.packages.Packages._process_dependencies")

    application_packages._add_aur(package_ahriman.base, set(), False)
    load_mock.assert_called_once()
    dependencies_mock.assert_called_once()


def test_add_directory(application_packages: Packages, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must add packages from directory
    """
    iterdir_mock = mocker.patch("pathlib.Path.iterdir",
                                return_value=[package.filepath for package in package_ahriman.packages.values()])
    copy_mock = mocker.patch("shutil.copy")

    application_packages._add_directory(package_ahriman.base)
    iterdir_mock.assert_called_once()
    copy_mock.assert_called_once()


def test_add_local(application_packages: Packages, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must add package from local sources
    """
    mocker.patch("ahriman.models.package.Package.load", return_value=package_ahriman)
    init_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.init")
    copytree_mock = mocker.patch("shutil.copytree")
    dependencies_mock = mocker.patch("ahriman.application.application.packages.Packages._process_dependencies")

    application_packages._add_local(package_ahriman.base, set(), False)
    init_mock.assert_called_once()
    copytree_mock.assert_has_calls([
        mock.call(Path(package_ahriman.base), application_packages.repository.paths.cache_for(package_ahriman.base)),
        mock.call(application_packages.repository.paths.cache_for(package_ahriman.base),
                  application_packages.repository.paths.manual_for(package_ahriman.base)),
    ])
    dependencies_mock.assert_called_once()


def test_add_remote(application_packages: Packages, package_description_ahriman: PackageDescription,
                    mocker: MockerFixture) -> None:
    """
    must add package from remote source
    """
    response_mock = MagicMock()
    response_mock.iter_content.return_value = ["chunk"]
    open_mock = mocker.patch("pathlib.Path.open")
    request_mock = mocker.patch("requests.get", return_value=response_mock)
    url = f"https://host/{package_description_ahriman.filename}"

    application_packages._add_remote(url)
    open_mock.assert_called_once_with("wb")
    request_mock.assert_called_once_with(url, stream=True)
    response_mock.raise_for_status.assert_called_once()


def test_process_dependencies(application_packages: Packages, mocker: MockerFixture) -> None:
    """
    must process dependencies addition
    """
    missing = {"python"}
    path = Path("local")
    dependencies_mock = mocker.patch("ahriman.models.package.Package.dependencies", return_value=missing)
    add_mock = mocker.patch("ahriman.application.application.packages.Packages.add")

    application_packages._process_dependencies(path, set(), False)
    dependencies_mock.assert_called_once_with(path)
    add_mock.assert_called_once_with(missing, PackageSource.AUR, False)


def test_process_dependencies_missing(application_packages: Packages, mocker: MockerFixture) -> None:
    """
    must process dependencies addition only for missing packages
    """
    path = Path("local")
    dependencies_mock = mocker.patch("ahriman.models.package.Package.dependencies",
                                     return_value={"python", "python-aiohttp"})
    add_mock = mocker.patch("ahriman.application.application.packages.Packages.add")

    application_packages._process_dependencies(path, {"python"}, False)
    dependencies_mock.assert_called_once_with(path)
    add_mock.assert_called_once_with({"python-aiohttp"}, PackageSource.AUR, False)


def test_process_dependencies_skip(application_packages: Packages, mocker: MockerFixture) -> None:
    """
    must skip dependencies processing
    """
    dependencies_mock = mocker.patch("ahriman.models.package.Package.dependencies")
    add_mock = mocker.patch("ahriman.application.application.packages.Packages.add")

    application_packages._process_dependencies(Path("local"), set(), True)
    dependencies_mock.assert_not_called()
    add_mock.assert_not_called()


def test_add_add_archive(application_packages: Packages, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must add package from archive via add function
    """
    mocker.patch("ahriman.application.application.packages.Packages._known_packages", return_value=set())
    add_mock = mocker.patch("ahriman.application.application.packages.Packages._add_archive")

    application_packages.add([package_ahriman.base], PackageSource.Archive, False)
    add_mock.assert_called_once()


def test_add_add_aur(application_packages: Packages, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must add package from AUR via add function
    """
    mocker.patch("ahriman.application.application.packages.Packages._known_packages", return_value=set())
    add_mock = mocker.patch("ahriman.application.application.packages.Packages._add_aur")

    application_packages.add([package_ahriman.base], PackageSource.AUR, True)
    add_mock.assert_called_once()


def test_add_add_directory(application_packages: Packages, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must add packages from directory via add function
    """
    mocker.patch("ahriman.application.application.packages.Packages._known_packages", return_value=set())
    add_mock = mocker.patch("ahriman.application.application.packages.Packages._add_directory")

    application_packages.add([package_ahriman.base], PackageSource.Directory, False)
    add_mock.assert_called_once()


def test_add_add_local(application_packages: Packages, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must add package from local sources via add function
    """
    mocker.patch("ahriman.application.application.packages.Packages._known_packages", return_value=set())
    add_mock = mocker.patch("ahriman.application.application.packages.Packages._add_local")

    application_packages.add([package_ahriman.base], PackageSource.Local, False)
    add_mock.assert_called_once()


def test_add_add_remote(application_packages: Packages, package_description_ahriman: PackageDescription,
                        mocker: MockerFixture) -> None:
    """
    must add package from remote source via add function
    """
    mocker.patch("ahriman.application.application.packages.Packages._known_packages", return_value=set())
    add_mock = mocker.patch("ahriman.application.application.packages.Packages._add_remote")
    url = f"https://host/{package_description_ahriman.filename}"

    application_packages.add([url], PackageSource.Remote, False)
    add_mock.assert_called_once()


def test_remove(application_packages: Packages, mocker: MockerFixture) -> None:
    """
    must remove package
    """
    executor_mock = mocker.patch("ahriman.core.repository.executor.Executor.process_remove")
    finalize_mock = mocker.patch("ahriman.application.application.packages.Packages._finalize")

    application_packages.remove([])
    executor_mock.assert_called_once()
    finalize_mock.assert_called_once()