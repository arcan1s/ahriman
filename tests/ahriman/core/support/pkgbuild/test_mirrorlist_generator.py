from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.support.pkgbuild.mirrorlist_generator import MirrorlistGenerator


def test_init_path(configuration: Configuration) -> None:
    """
    must set relative path to mirrorlist
    """
    _, repository_id = configuration.check_loaded()

    assert MirrorlistGenerator(repository_id, configuration, "mirrorlist").path == \
        Path("etc") / "pacman.d" / "aur-clone-mirrorlist"

    configuration.set_option("mirrorlist", "path", "/etc")
    assert MirrorlistGenerator(repository_id, configuration, "mirrorlist").path == Path("etc")


def test_license(configuration: Configuration) -> None:
    """
    must generate correct licenses list
    """
    _, repository_id = configuration.check_loaded()

    assert MirrorlistGenerator(repository_id, configuration, "mirrorlist").license == ["Unlicense"]

    configuration.set_option("mirrorlist", "license", "GPL MPL")
    assert MirrorlistGenerator(repository_id, configuration, "mirrorlist").license == ["GPL", "MPL"]


def test_pkgdesc(configuration: Configuration) -> None:
    """
    must generate correct pkgdesc property
    """
    _, repository_id = configuration.check_loaded()

    assert MirrorlistGenerator(repository_id, configuration, "mirrorlist").pkgdesc == \
        "aur-clone mirror list for use by pacman"

    configuration.set_option("mirrorlist", "description", "description")
    assert MirrorlistGenerator(repository_id, configuration, "mirrorlist").pkgdesc == "description"


def test_pkgname(configuration: Configuration) -> None:
    """
    must generate correct pkgname property
    """
    _, repository_id = configuration.check_loaded()

    assert MirrorlistGenerator(repository_id, configuration, "mirrorlist").pkgname == "aur-clone-mirrorlist"

    configuration.set_option("mirrorlist", "package", "mirrorlist")
    assert MirrorlistGenerator(repository_id, configuration, "mirrorlist").pkgname == "mirrorlist"


def test_url(configuration: Configuration) -> None:
    """
    must generate correct url property
    """
    _, repository_id = configuration.check_loaded()

    assert MirrorlistGenerator(repository_id, configuration, "mirrorlist").url == ""

    configuration.set_option("mirrorlist", "homepage", "homepage")
    assert MirrorlistGenerator(repository_id, configuration, "mirrorlist").url == "homepage"


def test_generate_mirrorlist(mirrorlist_generator: MirrorlistGenerator, mocker: MockerFixture) -> None:
    """
    must correctly generate mirrorlist file
    """
    write_mock = mocker.patch("pathlib.Path.write_text")
    mirrorlist_generator._generate_mirrorlist(Path("local"))
    write_mock.assert_called_once_with("Server = http://localhost\n", encoding="utf8")


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
