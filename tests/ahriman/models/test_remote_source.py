from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource
from ahriman.models.remote_source import RemoteSource


def test_post_init(remote_source: RemoteSource) -> None:
    """
    must convert string source to enum
    """
    remote = RemoteSource(
        git_url=remote_source.git_url,
        web_url=remote_source.web_url,
        path=remote_source.path,
        branch=remote_source.branch,
        source=remote_source.source.value,
    )
    assert remote == remote_source


def test_pkgbuild_dir(remote_source: RemoteSource) -> None:
    """
    must return path as is in `path` property
    """
    assert isinstance(remote_source.pkgbuild_dir, Path)
    assert remote_source.pkgbuild_dir.name == ""


def test_from_json(remote_source: RemoteSource) -> None:
    """
    must construct remote source from json
    """
    assert RemoteSource.from_json(remote_source.view()) == remote_source


def test_from_json_empty() -> None:
    """
    must return None in case of empty dictionary, which is required by the database wrapper
    """
    assert RemoteSource.from_json({}) is None


def test_from_source_aur(package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must construct remote from AUR source
    """
    remote_git_url_mock = mocker.patch("ahriman.core.alpm.remote.AUR.remote_git_url")
    remote_web_url_mock = mocker.patch("ahriman.core.alpm.remote.AUR.remote_web_url")

    remote = RemoteSource.from_source(PackageSource.AUR, package_ahriman.base, "aur")
    remote_git_url_mock.assert_called_once_with(package_ahriman.base, "aur")
    remote_web_url_mock.assert_called_once_with(package_ahriman.base)
    assert remote.pkgbuild_dir == Path(".")
    assert remote.branch == "master"
    assert remote.source == PackageSource.AUR


def test_from_source_official(package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must construct remote from official repository source
    """
    remote_git_url_mock = mocker.patch("ahriman.core.alpm.remote.Official.remote_git_url")
    remote_web_url_mock = mocker.patch("ahriman.core.alpm.remote.Official.remote_web_url")

    remote = RemoteSource.from_source(PackageSource.Repository, package_ahriman.base, "community")
    remote_git_url_mock.assert_called_once_with(package_ahriman.base, "community")
    remote_web_url_mock.assert_called_once_with(package_ahriman.base)
    assert remote.pkgbuild_dir == Path("trunk")
    assert remote.branch.endswith(package_ahriman.base)
    assert remote.source == PackageSource.Repository


def test_from_source_other() -> None:
    """
    must return None in case if source is not one of AUR or Repository
    """
    assert RemoteSource.from_source(PackageSource.Archive, "package", "repository") is None
    assert RemoteSource.from_source(PackageSource.Directory, "package", "repository") is None
    assert RemoteSource.from_source(PackageSource.Local, "package", "repository") is None
    assert RemoteSource.from_source(PackageSource.Remote, "package", "repository") is None
