import pytest

from pathlib import Path

from ahriman.core.exceptions import InitializeError
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


def test_is_remote() -> None:
    """
    must correctly define if source is remote or not
    """
    for source in PackageSource:
        assert RemoteSource(source=source).is_remote or source not in (PackageSource.AUR, PackageSource.Repository)


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


def test_git_source(remote_source: RemoteSource) -> None:
    """
    must correctly return git source
    """
    assert remote_source.git_source() == (remote_source.git_url, remote_source.branch)


def test_git_source_empty() -> None:
    """
    must raise exception if path is none
    """
    with pytest.raises(InitializeError):
        RemoteSource(source=PackageSource.Remote).git_source()
