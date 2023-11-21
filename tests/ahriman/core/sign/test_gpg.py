import pytest
import requests

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.sign.gpg import GPG
from ahriman.models.sign_settings import SignSettings


def test_repository_sign_args_1(gpg_with_key: GPG) -> None:
    """
    must generate correct sign args
    """
    gpg_with_key.targets = {SignSettings.Repository}
    assert gpg_with_key.repository_sign_args


def test_repository_sign_args_2(gpg_with_key: GPG) -> None:
    """
    must generate correct sign args
    """
    gpg_with_key.targets = {SignSettings.Packages, SignSettings.Repository}
    assert gpg_with_key.repository_sign_args


def test_repository_sign_args_skip_1(gpg_with_key: GPG) -> None:
    """
    must return empty args if it is not set
    """
    gpg_with_key.targets = {}
    assert not gpg_with_key.repository_sign_args


def test_repository_sign_args_skip_2(gpg_with_key: GPG) -> None:
    """
    must return empty args if it is not set
    """
    gpg_with_key.targets = {SignSettings.Packages}
    assert not gpg_with_key.repository_sign_args


def test_repository_sign_args_skip_3(gpg: GPG) -> None:
    """
    must return empty args if it is not set
    """
    gpg.targets = {SignSettings.Repository}
    assert not gpg.repository_sign_args


def test_repository_sign_args_skip_4(gpg: GPG) -> None:
    """
    must return empty args if it is not set
    """
    gpg.targets = {SignSettings.Packages, SignSettings.Repository}
    assert not gpg.repository_sign_args


def test_sign_command(gpg_with_key: GPG) -> None:
    """
    must generate sign command
    """
    assert gpg_with_key.sign_command(Path("a"), gpg_with_key.default_key)


def test_sign_options(configuration: Configuration) -> None:
    """
    must correctly parse sign options
    """
    configuration.set_option("sign", "target", "repository disabled")
    configuration.set_option("sign", "key", "default-key")

    target, default_key = GPG.sign_options(configuration)
    assert target == {SignSettings.Repository}
    assert default_key == "default-key"


def test_signature() -> None:
    """
    must correctly generate the signature path
    """
    assert GPG.signature(Path("path") / "to" / "package.tar.xz") == Path("path") / "to" / "package.tar.xz.sig"


def test_key_download(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must download the key from public server
    """
    requests_mock = mocker.patch("ahriman.core.sign.gpg.GPG.make_request")
    gpg.key_download("keyserver.ubuntu.com", "0xE989490C")
    requests_mock.assert_called_once_with(
        "GET", "https://keyserver.ubuntu.com/pks/lookup",
        params=[("op", "get"), ("options", "mr"), ("search", "0xE989490C")])


def test_key_download_failure(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must download the key from public server and log error if any (and raise it again)
    """
    mocker.patch("requests.Session.request", side_effect=requests.HTTPError())
    with pytest.raises(requests.HTTPError):
        gpg.key_download("keyserver.ubuntu.com", "0xE989490C")


def test_key_export(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must export gpg key correctly
    """
    check_output_mock = mocker.patch("ahriman.core.sign.gpg.check_output", return_value="key")
    assert gpg.key_export("k") == "key"
    check_output_mock.assert_called_once_with("gpg", "--armor", "--no-emit-version", "--export", "k", logger=gpg.logger)


def test_key_fingerprint(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must extract fingerprint
    """
    check_output_mock = mocker.patch(
        "ahriman.core.sign.gpg.check_output",
        return_value="""tru::1:1576103830:0:3:1:5
fpr:::::::::C6EBB9222C3C8078631A0DE4BD2AC8C5E989490C:
sub:-:4096:1:7E3A4240CE3C45C2:1615121387::::::e::::::23:
fpr:::::::::43A663569A07EE1E4ECC55CC7E3A4240CE3C45C2:""")

    key = "0xCE3C45C2"
    assert gpg.key_fingerprint(key) == "C6EBB9222C3C8078631A0DE4BD2AC8C5E989490C"
    check_output_mock.assert_called_once_with("gpg", "--with-colons", "--fingerprint", key, logger=gpg.logger)


def test_key_import(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must import PGP key from the server
    """
    mocker.patch("ahriman.core.sign.gpg.GPG.key_download", return_value="key")
    check_output_mock = mocker.patch("ahriman.core.sign.gpg.check_output")

    gpg.key_import("keyserver.ubuntu.com", "0xE989490C")
    check_output_mock.assert_called_once_with("gpg", "--import", input_data="key", logger=gpg.logger)


def test_process(gpg_with_key: GPG, mocker: MockerFixture) -> None:
    """
    must call process method correctly
    """
    result = [Path("a"), Path("a.sig")]
    check_output_mock = mocker.patch("ahriman.core.sign.gpg.check_output")

    assert gpg_with_key.process(Path("a"), gpg_with_key.default_key) == result
    check_output_mock.assert_called()


def test_process_sign_package_1(gpg_with_key: GPG, mocker: MockerFixture) -> None:
    """
    must sign package
    """
    result = [Path("a"), Path("a.sig")]
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process", return_value=result)

    gpg_with_key.targets = {SignSettings.Packages}
    assert gpg_with_key.process_sign_package(Path("a"), "a") == result
    process_mock.assert_called_once_with(Path("a"), "a")


def test_process_sign_package_2(gpg_with_key: GPG, mocker: MockerFixture) -> None:
    """
    must sign package if there are multiple targets
    """
    result = [Path("a"), Path("a.sig")]
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process", return_value=result)

    gpg_with_key.targets = {SignSettings.Packages, SignSettings.Repository}
    assert gpg_with_key.process_sign_package(Path("a"), "a") == result
    process_mock.assert_called_once_with(Path("a"), "a")


def test_process_sign_package_3(gpg_with_key: GPG, mocker: MockerFixture) -> None:
    """
    must sign package with default key if none passed
    """
    result = [Path("a"), Path("a.sig")]
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process", return_value=result)

    gpg_with_key.targets = {SignSettings.Packages}
    assert gpg_with_key.process_sign_package(Path("a"), None) == result
    process_mock.assert_called_once_with(Path("a"), gpg_with_key.default_key)


def test_process_sign_package_skip_1(gpg_with_key: GPG, mocker: MockerFixture) -> None:
    """
    must not sign package if it is not set
    """
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")
    gpg_with_key.targets = {}
    gpg_with_key.process_sign_package(Path("a"), "a")
    process_mock.assert_not_called()


def test_process_sign_package_skip_2(gpg_with_key: GPG, mocker: MockerFixture) -> None:
    """
    must not sign package if it is not set
    """
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")
    gpg_with_key.targets = {SignSettings.Repository}
    gpg_with_key.process_sign_package(Path("a"), "a")
    process_mock.assert_not_called()


def test_process_sign_package_skip_3(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must not sign package if it is not set
    """
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")
    gpg.targets = {SignSettings.Packages}
    gpg.process_sign_package(Path("a"), None)
    process_mock.assert_not_called()


def test_process_sign_package_skip_4(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must not sign package if it is not set
    """
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")
    gpg.targets = {SignSettings.Packages, SignSettings.Repository}
    gpg.process_sign_package(Path("a"), None)
    process_mock.assert_not_called()


def test_process_sign_package_skip_already_signed(gpg_with_key: GPG, mocker: MockerFixture) -> None:
    """
    must not sign package if it was already signed
    """
    result = [Path("a"), Path("a.sig")]
    mocker.patch("pathlib.Path.is_file", return_value=True)
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")

    assert gpg_with_key.process_sign_package(Path("a"), gpg_with_key.default_key) == result
    process_mock.assert_not_called()


def test_process_sign_repository_1(gpg_with_key: GPG, mocker: MockerFixture) -> None:
    """
    must sign repository
    """
    result = [Path("a"), Path("a.sig")]
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process", return_value=result)

    gpg_with_key.targets = {SignSettings.Repository}
    assert gpg_with_key.process_sign_repository(Path("a")) == result
    process_mock.assert_called_once_with(Path("a"), "key")


def test_process_sign_repository_2(gpg_with_key: GPG, mocker: MockerFixture) -> None:
    """
    must sign repository if there are multiple targets
    """
    result = [Path("a"), Path("a.sig")]
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process", return_value=result)

    gpg_with_key.targets = {SignSettings.Packages, SignSettings.Repository}
    assert gpg_with_key.process_sign_repository(Path("a")) == result
    process_mock.assert_called_once_with(Path("a"), "key")


def test_process_sign_repository_skip_1(gpg_with_key: GPG, mocker: MockerFixture) -> None:
    """
    must not sign repository if it is not set
    """
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")
    gpg_with_key.targets = {}
    gpg_with_key.process_sign_repository(Path("a"))
    process_mock.assert_not_called()


def test_process_sign_repository_skip_2(gpg_with_key: GPG, mocker: MockerFixture) -> None:
    """
    must not sign repository if it is not set
    """
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")
    gpg_with_key.targets = {SignSettings.Packages}
    gpg_with_key.process_sign_repository(Path("a"))
    process_mock.assert_not_called()


def test_process_sign_repository_skip_3(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must not sign repository if it is not set
    """
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")
    gpg.targets = {SignSettings.Repository}
    gpg.process_sign_repository(Path("a"))
    process_mock.assert_not_called()


def test_process_sign_repository_skip_4(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must not sign repository if it is not set
    """
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")
    gpg.targets = {SignSettings.Packages, SignSettings.Repository}
    gpg.process_sign_repository(Path("a"))
    process_mock.assert_not_called()
