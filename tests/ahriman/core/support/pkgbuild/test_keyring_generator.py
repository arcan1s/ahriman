import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import MagicMock, call as MockCall

from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.exceptions import PkgbuildGeneratorError
from ahriman.core.sign.gpg import GPG
from ahriman.core.support.pkgbuild.keyring_generator import KeyringGenerator
from ahriman.models.user import User


def test_init_packagers(database: SQLite, gpg: GPG, configuration: Configuration, user: User,
                        mocker: MockerFixture) -> None:
    """
    must extract packagers keys
    """
    mocker.patch("ahriman.core.database.SQLite.user_list", return_value=[user])
    _, repository_id = configuration.check_loaded()

    assert KeyringGenerator(database, gpg, repository_id, configuration, "keyring").packagers == ["key"]

    configuration.set_option("keyring", "packagers", "key1")
    assert KeyringGenerator(database, gpg, repository_id, configuration, "keyring").packagers == ["key1"]


def test_init_revoked(database: SQLite, gpg: GPG, configuration: Configuration) -> None:
    """
    must extract revoked keys
    """
    _, repository_id = configuration.check_loaded()

    assert KeyringGenerator(database, gpg, repository_id, configuration, "keyring").revoked == []

    configuration.set_option("keyring", "revoked", "key1")
    assert KeyringGenerator(database, gpg, repository_id, configuration, "keyring").revoked == ["key1"]


def test_init_trusted(database: SQLite, gpg: GPG, configuration: Configuration) -> None:
    """
    must extract trusted keys
    """
    _, repository_id = configuration.check_loaded()

    assert KeyringGenerator(database, gpg, repository_id, configuration, "keyring").trusted == []

    gpg.default_key = "key"
    assert KeyringGenerator(database, gpg, repository_id, configuration, "keyring").trusted == ["key"]

    configuration.set_option("keyring", "trusted", "key1")
    assert KeyringGenerator(database, gpg, repository_id, configuration, "keyring").trusted == ["key1"]


def test_license(database: SQLite, gpg: GPG, configuration: Configuration) -> None:
    """
    must generate correct licenses list
    """
    _, repository_id = configuration.check_loaded()

    assert KeyringGenerator(database, gpg, repository_id, configuration, "keyring").license == ["Unlicense"]

    configuration.set_option("keyring", "license", "GPL MPL")
    assert KeyringGenerator(database, gpg, repository_id, configuration, "keyring").license == ["GPL", "MPL"]


def test_pkgdesc(database: SQLite, gpg: GPG, configuration: Configuration) -> None:
    """
    must generate correct pkgdesc property
    """
    _, repository_id = configuration.check_loaded()

    assert KeyringGenerator(database, gpg, repository_id, configuration, "keyring").pkgdesc == "aur-clone PGP keyring"

    configuration.set_option("keyring", "description", "description")
    assert KeyringGenerator(database, gpg, repository_id, configuration, "keyring").pkgdesc == "description"


def test_pkgname(database: SQLite, gpg: GPG, configuration: Configuration) -> None:
    """
    must generate correct pkgname property
    """
    _, repository_id = configuration.check_loaded()

    assert KeyringGenerator(database, gpg, repository_id, configuration, "keyring").pkgname == "aur-clone-keyring"

    configuration.set_option("keyring", "package", "keyring")
    assert KeyringGenerator(database, gpg, repository_id, configuration, "keyring").pkgname == "keyring"


def test_url(database: SQLite, gpg: GPG, configuration: Configuration) -> None:
    """
    must generate correct url property
    """
    _, repository_id = configuration.check_loaded()

    assert KeyringGenerator(database, gpg, repository_id, configuration, "keyring").url == ""

    configuration.set_option("keyring", "homepage", "homepage")
    assert KeyringGenerator(database, gpg, repository_id, configuration, "keyring").url == "homepage"


def test_generate_gpg(keyring_generator: KeyringGenerator, mocker: MockerFixture) -> None:
    """
    must correctly generate file with all PGP keys
    """
    file_mock = MagicMock()
    export_mock = mocker.patch("ahriman.core.sign.gpg.GPG.key_export", side_effect=lambda key: key)
    open_mock = mocker.patch("pathlib.Path.open")
    open_mock.return_value.__enter__.return_value = file_mock
    keyring_generator.packagers = ["key"]
    keyring_generator.revoked = ["revoked"]
    keyring_generator.trusted = ["trusted", "key"]

    keyring_generator._generate_gpg(Path("local"))
    open_mock.assert_called_once_with("w")
    export_mock.assert_has_calls([MockCall("key"), MockCall("revoked"), MockCall("trusted")])
    file_mock.write.assert_has_calls([
        MockCall("key"), MockCall("\n"),
        MockCall("revoked"), MockCall("\n"),
        MockCall("trusted"), MockCall("\n"),
    ])


def test_generate_revoked(keyring_generator: KeyringGenerator, mocker: MockerFixture) -> None:
    """
    must correctly generate file with revoked keys
    """
    file_mock = MagicMock()
    fingerprint_mock = mocker.patch("ahriman.core.sign.gpg.GPG.key_fingerprint", side_effect=lambda key: key)
    open_mock = mocker.patch("pathlib.Path.open")
    open_mock.return_value.__enter__.return_value = file_mock
    keyring_generator.revoked = ["revoked"]

    keyring_generator._generate_revoked(Path("local"))
    open_mock.assert_called_once_with("w")
    fingerprint_mock.assert_called_once_with("revoked")
    file_mock.write.assert_has_calls([MockCall("revoked"), MockCall("\n")])


def test_generate_trusted(keyring_generator: KeyringGenerator, mocker: MockerFixture) -> None:
    """
    must correctly generate file with trusted keys
    """
    file_mock = MagicMock()
    fingerprint_mock = mocker.patch("ahriman.core.sign.gpg.GPG.key_fingerprint", side_effect=lambda key: key)
    open_mock = mocker.patch("pathlib.Path.open")
    open_mock.return_value.__enter__.return_value = file_mock
    keyring_generator.trusted = ["trusted", "trusted"]

    keyring_generator._generate_trusted(Path("local"))
    open_mock.assert_called_once_with("w")
    fingerprint_mock.assert_called_once_with("trusted")
    file_mock.write.assert_has_calls([MockCall("trusted"), MockCall(":4:\n")])


def test_generate_trusted_empty(keyring_generator: KeyringGenerator) -> None:
    """
    must raise PkgbuildGeneratorError if no trusted keys set
    """
    with pytest.raises(PkgbuildGeneratorError):
        keyring_generator._generate_trusted(Path("local"))


def test_install(keyring_generator: KeyringGenerator) -> None:
    """
    must return install functions
    """
    assert keyring_generator.install() == """post_upgrade() {
  if usr/bin/pacman-key -l >/dev/null 2>&1; then
    usr/bin/pacman-key --populate aur-clone
    usr/bin/pacman-key --updatedb
  fi
}

post_install() {
  if [ -x usr/bin/pacman-key ]; then
    post_upgrade
  fi
}"""


def test_package(keyring_generator: KeyringGenerator) -> None:
    """
    must generate package function correctly
    """
    assert keyring_generator.package() == """{
  install -Dm644 "$srcdir/aur-clone.gpg" "$pkgdir/usr/share/pacman/keyrings/aur-clone.gpg"
  install -Dm644 "$srcdir/aur-clone-revoked" "$pkgdir/usr/share/pacman/keyrings/aur-clone-revoked"
  install -Dm644 "$srcdir/aur-clone-trusted" "$pkgdir/usr/share/pacman/keyrings/aur-clone-trusted"
}"""


def test_sources(keyring_generator: KeyringGenerator) -> None:
    """
    must return valid sources files list
    """
    assert keyring_generator.sources().get("aur-clone.gpg")
    assert keyring_generator.sources().get("aur-clone-revoked")
    assert keyring_generator.sources().get("aur-clone-trusted")
