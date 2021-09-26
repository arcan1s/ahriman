from pytest_mock import MockerFixture

from ahriman.models.package_source import PackageSource


def test_resolve_non_auto() -> None:
    """
    must resolve non auto type to itself
    """
    for source in filter(lambda src: src != PackageSource.Auto, PackageSource):
        assert source.resolve("") == source


def test_resolve_archive(mocker: MockerFixture) -> None:
    """
    must resolve auto type into the archive
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    mocker.patch("pathlib.Path.is_file", return_value=True)
    assert PackageSource.Auto.resolve("linux-5.14.2.arch1-2-x86_64.pkg.tar.zst") == PackageSource.Archive


def test_resolve_directory(mocker: MockerFixture) -> None:
    """
    must resolve auto type into the directory
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("pathlib.Path.is_file", return_value=False)
    assert PackageSource.Auto.resolve("path") == PackageSource.Directory


def test_resolve_aur(mocker: MockerFixture) -> None:
    """
    must resolve auto type into the AUR package
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    mocker.patch("pathlib.Path.is_file", return_value=False)
    assert PackageSource.Auto.resolve("package") == PackageSource.AUR


def test_resolve_aur_not_package_like(mocker: MockerFixture) -> None:
    """
    must resolve auto type into the AUR package if it is file, but does not look like a package archive
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    mocker.patch("pathlib.Path.is_file", return_value=True)
    assert PackageSource.Auto.resolve("package") == PackageSource.AUR
