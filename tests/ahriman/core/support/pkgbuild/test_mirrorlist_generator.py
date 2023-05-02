from pathlib import Path
from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.support.pkgbuild.mirrorlist_generator import MirrorlistGenerator


def test_init_path(configuration: Configuration) -> None:
    """
    must set relative path to mirrorlist
    """
    assert MirrorlistGenerator(configuration, "mirrorlist").path == Path("etc") / "pacman.d" / "aur-clone-mirrorlist"

    configuration.set_option("mirrorlist", "path", "/etc")
    assert MirrorlistGenerator(configuration, "mirrorlist").path == Path("etc")


def test_license(configuration: Configuration) -> None:
    """
    must generate correct licenses list
    """
    assert MirrorlistGenerator(configuration, "mirrorlist").license == ["Unlicense"]

    configuration.set_option("mirrorlist", "license", "GPL MPL")
    assert MirrorlistGenerator(configuration, "mirrorlist").license == ["GPL", "MPL"]


def test_pkgdesc(configuration: Configuration) -> None:
    """
    must generate correct pkgdesc property
    """
    assert MirrorlistGenerator(configuration, "mirrorlist").pkgdesc == "aur-clone mirror list for use by pacman"

    configuration.set_option("mirrorlist", "description", "description")
    assert MirrorlistGenerator(configuration, "mirrorlist").pkgdesc == "description"


def test_pkgname(configuration: Configuration) -> None:
    """
    must generate correct pkgname property
    """
    assert MirrorlistGenerator(configuration, "mirrorlist").pkgname == "aur-clone-mirrorlist"

    configuration.set_option("mirrorlist", "package", "mirrorlist")
    assert MirrorlistGenerator(configuration, "mirrorlist").pkgname == "mirrorlist"


def test_url(configuration: Configuration) -> None:
    """
    must generate correct url property
    """
    assert MirrorlistGenerator(configuration, "mirrorlist").url == ""

    configuration.set_option("mirrorlist", "homepage", "homepage")
    assert MirrorlistGenerator(configuration, "mirrorlist").url == "homepage"


def test_generate_mirrorlist(mirrorlist_generator: MirrorlistGenerator, mocker: MockerFixture) -> None:
    """
    must correctly generate mirrorlist file
    """
    path = Path("local")
    file_mock = MagicMock()
    open_mock = mocker.patch("pathlib.Path.open")
    open_mock.return_value.__enter__.return_value = file_mock

    mirrorlist_generator._generate_mirrorlist(path)
    open_mock.assert_called_once_with("w")
    file_mock.writelines.assert_called_once_with(["Server = http://localhost\n"])


def test_package(mirrorlist_generator: MirrorlistGenerator) -> None:
    """
    must generate package function correctly
    """
    assert mirrorlist_generator.package() == """{
  install -Dm644 "$srcdir/mirrorlist" "$pkgdir/etc/pacman.d/aur-clone-mirrorlist"
}"""


def test_patches(mirrorlist_generator: MirrorlistGenerator) -> None:
    """
    must generate additional patch list
    """
    patches = {patch.key: patch for patch in mirrorlist_generator.patches()}

    assert "backup" in patches
    assert patches["backup"].value == [str(mirrorlist_generator.path)]


def test_sources(mirrorlist_generator: MirrorlistGenerator) -> None:
    """
    must return valid sources files list
    """
    assert mirrorlist_generator.sources().get("mirrorlist")
