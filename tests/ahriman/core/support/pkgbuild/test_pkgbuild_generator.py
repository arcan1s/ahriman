import datetime
import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import MagicMock, call as MockCall

from ahriman.core.support.pkgbuild.pkgbuild_generator import PkgbuildGenerator
from ahriman.core.util import utcnow
from ahriman.models.pkgbuild_patch import PkgbuildPatch


def test_license(pkgbuild_generator: PkgbuildGenerator) -> None:
    """
    must return empty license list
    """
    assert pkgbuild_generator.license == []


def test_pkgdesc(pkgbuild_generator: PkgbuildGenerator) -> None:
    """
    must raise NotImplementedError on missing pkgdesc property
    """
    with pytest.raises(NotImplementedError):
        assert pkgbuild_generator.pkgdesc


def test_pkgname(pkgbuild_generator: PkgbuildGenerator) -> None:
    """
    must raise NotImplementedError on missing pkgname property
    """
    with pytest.raises(NotImplementedError):
        assert pkgbuild_generator.pkgname


def test_pkgver(pkgbuild_generator: PkgbuildGenerator, mocker: MockerFixture) -> None:
    """
    must implement default version as current date
    """
    mocker.patch("ahriman.core.support.pkgbuild.pkgbuild_generator.utcnow", return_value=datetime.datetime(2002, 3, 11))
    assert pkgbuild_generator.pkgver == utcnow().strftime("20020311")


def test_url(pkgbuild_generator: PkgbuildGenerator) -> None:
    """
    must return empty url
    """
    assert pkgbuild_generator.url == ""


def test_install(pkgbuild_generator: PkgbuildGenerator) -> None:
    """
    must return empty install function
    """
    assert pkgbuild_generator.install() is None


def test_package(pkgbuild_generator: PkgbuildGenerator) -> None:
    """
    must raise NotImplementedError on missing package function
    """
    with pytest.raises(NotImplementedError):
        pkgbuild_generator.package()


def test_patches(pkgbuild_generator: PkgbuildGenerator) -> None:
    """
    must return empty patches list
    """
    assert pkgbuild_generator.patches() == []


def test_sources(pkgbuild_generator: PkgbuildGenerator) -> None:
    """
    must return empty sources list
    """
    assert pkgbuild_generator.sources() == {}


def test_write_install(pkgbuild_generator: PkgbuildGenerator, mocker: MockerFixture) -> None:
    """
    must write install file
    """
    mocker.patch.object(PkgbuildGenerator, "pkgname", "package")
    mocker.patch("ahriman.core.support.pkgbuild.pkgbuild_generator.PkgbuildGenerator.install", return_value="content")
    write_mock = mocker.patch("pathlib.Path.write_text")

    assert pkgbuild_generator.write_install(Path("local")) == [PkgbuildPatch("install", "package.install")]
    write_mock.assert_called_once_with("content")


def test_write_install_empty(pkgbuild_generator: PkgbuildGenerator) -> None:
    """
    must return empty patch list for missing install function
    """
    assert pkgbuild_generator.write_install(Path("local")) == []


def test_write_pkgbuild(pkgbuild_generator: PkgbuildGenerator, mocker: MockerFixture) -> None:
    """
    must write PKGBUILD content to file
    """
    path = Path("local")
    for prop in ("pkgdesc", "pkgname"):
        mocker.patch.object(PkgbuildGenerator, prop, "")
    mocker.patch("ahriman.core.support.pkgbuild.pkgbuild_generator.PkgbuildGenerator.package", return_value="{}")
    patches_mock = mocker.patch("ahriman.core.support.pkgbuild.pkgbuild_generator.PkgbuildGenerator.patches",
                                return_value=[PkgbuildPatch("property", "value")])
    install_mock = mocker.patch("ahriman.core.support.pkgbuild.pkgbuild_generator.PkgbuildGenerator.write_install",
                                return_value=[PkgbuildPatch("install", "pkgname.install")])
    sources_mock = mocker.patch("ahriman.core.support.pkgbuild.pkgbuild_generator.PkgbuildGenerator.write_sources",
                                return_value=[PkgbuildPatch("source", []), PkgbuildPatch("sha512sums", [])])
    write_mock = mocker.patch("ahriman.models.pkgbuild_patch.PkgbuildPatch.write")

    pkgbuild_generator.write_pkgbuild(path)
    patches_mock.assert_called_once_with()
    install_mock.assert_called_once_with(path)
    sources_mock.assert_called_once_with(path)
    write_mock.assert_has_calls([MockCall(path / "PKGBUILD")] * 12)


def test_write_sources(pkgbuild_generator: PkgbuildGenerator, mocker: MockerFixture) -> None:
    """
    must write sources files
    """
    path = Path("local")
    generator_mock = MagicMock()
    sources_mock = mocker.patch("ahriman.core.support.pkgbuild.pkgbuild_generator.PkgbuildGenerator.sources",
                                return_value={"source": generator_mock})
    open_mock = mocker.patch("pathlib.Path.open")
    hash_mock = MagicMock()
    hash_mock.hexdigest.return_value = "hash"
    mocker.patch("hashlib.sha512", return_value=hash_mock)

    assert pkgbuild_generator.write_sources(path) == [
        PkgbuildPatch("source", ["source"]),
        PkgbuildPatch("sha512sums", ["hash"]),
    ]
    generator_mock.assert_called_once_with(path / "source")
    sources_mock.assert_called_once_with()
    open_mock.assert_called_once_with("rb")
