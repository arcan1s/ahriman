from collections.abc import Callable
from pytest_mock import MockerFixture
from pathlib import Path

from ahriman.models.package_description import PackageDescription
from ahriman.models.package_source import PackageSource
from ahriman.models.repository_paths import RepositoryPaths


def _is_file_mock(is_any_file: bool, is_pkgbuild: bool) -> Callable[[Path], bool]:
    """
    helper to mock is_file method

    Args:
        is_any_file(bool): value which will be return for any file
        is_pkgbuild(bool): value which will be return if PKGBUILD like path asked

    Returns:
        Callable[[Path], bool]: side effect function for the mocker object
    """
    side_effect: Callable[[Path], bool] = lambda source: is_pkgbuild if source.name == "PKGBUILD" else is_any_file
    return side_effect


def test_resolve_non_auto(repository_paths: RepositoryPaths) -> None:
    """
    must resolve non auto type to itself
    """
    for source in filter(lambda src: src != PackageSource.Auto, PackageSource):
        assert source.resolve("", repository_paths) == source


def test_resolve_archive(package_description_ahriman: PackageDescription, repository_paths: RepositoryPaths,
                         mocker: MockerFixture) -> None:
    """
    must resolve auto type into the archive
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    mocker.patch("pathlib.Path.is_file", autospec=True, side_effect=_is_file_mock(True, False))
    assert PackageSource.Auto.resolve(package_description_ahriman.filename, repository_paths) == PackageSource.Archive


def test_resolve_aur(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must resolve auto type into the AUR package
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    mocker.patch("pathlib.Path.is_file", return_value=False)
    assert PackageSource.Auto.resolve("package", repository_paths) == PackageSource.AUR


def test_resolve_aur_not_package_like(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must resolve auto type into the AUR package if it is file, but does not look like a package archive
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    mocker.patch("pathlib.Path.is_file", autospec=True, side_effect=_is_file_mock(True, False))
    assert PackageSource.Auto.resolve("package", repository_paths) == PackageSource.AUR


def test_resolve_aur_no_access(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must resolve auto type into the AUR package in case if we cannot read in suggested path
    """
    mocker.patch("pathlib.Path.is_dir", side_effect=PermissionError())
    assert PackageSource.Auto.resolve("package", repository_paths) == PackageSource.AUR


def test_resolve_directory(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must resolve auto type into the directory
    """
    mocker.patch("pathlib.Path.is_dir", autospec=True, side_effect=lambda p: p == Path("path"))
    mocker.patch("pathlib.Path.is_file", autospec=True, side_effect=_is_file_mock(False, False))
    assert PackageSource.Auto.resolve("path", repository_paths) == PackageSource.Directory


def test_resolve_local(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must resolve auto type into the local sources
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    mocker.patch("pathlib.Path.is_file", autospec=True, side_effect=_is_file_mock(True, True))
    assert PackageSource.Auto.resolve("path", repository_paths) == PackageSource.Local


def test_resolve_local_cache(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must resolve auto type into the local sources
    """
    cache_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.cache_for", return_value=Path("cache"))
    mocker.patch("pathlib.Path.is_dir", autospec=True, side_effect=lambda p: p == Path("cache"))
    mocker.patch("pathlib.Path.is_file", autospec=True, side_effect=_is_file_mock(False, False))

    assert PackageSource.Auto.resolve("path", repository_paths) == PackageSource.Local
    cache_mock.assert_called_once_with("path")


def test_resolve_remote(package_description_ahriman: PackageDescription, repository_paths: RepositoryPaths,
                        mocker: MockerFixture) -> None:
    """
    must resolve auto type into the remote sources
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    mocker.patch("pathlib.Path.is_file", autospec=True, side_effect=_is_file_mock(False, False))
    url = f"https://host/{package_description_ahriman.filename}"
    assert PackageSource.Auto.resolve(url, repository_paths) == PackageSource.Remote
