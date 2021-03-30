from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.sign.gpg import GPG
from ahriman.models.sign_settings import SignSettings


def test_repository_sign_args_1(gpg_with_key: GPG) -> None:
    """
    must generate correct sign args
    """
    gpg_with_key.targets = {SignSettings.SignRepository}
    assert gpg_with_key.repository_sign_args


def test_repository_sign_args_2(gpg_with_key: GPG) -> None:
    """
    must generate correct sign args
    """
    gpg_with_key.targets = {SignSettings.SignPackages, SignSettings.SignRepository}
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
    gpg_with_key.targets = {SignSettings.SignPackages}
    assert not gpg_with_key.repository_sign_args


def test_repository_sign_args_skip_3(gpg: GPG) -> None:
    """
    must return empty args if it is not set
    """
    gpg.targets = {SignSettings.SignRepository}
    assert not gpg.repository_sign_args


def test_repository_sign_args_skip_4(gpg: GPG) -> None:
    """
    must return empty args if it is not set
    """
    gpg.targets = {SignSettings.SignPackages, SignSettings.SignRepository}
    assert not gpg.repository_sign_args


def test_sign_package_1(gpg_with_key: GPG, mocker: MockerFixture) -> None:
    """
    must sign package
    """
    result = [Path("a"), Path("a.sig")]
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process", return_value=result)

    gpg_with_key.targets = {SignSettings.SignPackages}
    assert gpg_with_key.sign_package(Path("a"), "a") == result
    process_mock.assert_called_once()


def test_sign_package_2(gpg_with_key: GPG, mocker: MockerFixture) -> None:
    """
    must sign package
    """
    result = [Path("a"), Path("a.sig")]
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process", return_value=result)

    gpg_with_key.targets = {SignSettings.SignPackages, SignSettings.SignRepository}
    assert gpg_with_key.sign_package(Path("a"), "a") == result
    process_mock.assert_called_once()


def test_sign_package_skip_1(gpg_with_key: GPG, mocker: MockerFixture) -> None:
    """
    must not sign package if it is not set
    """
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")
    gpg_with_key.targets = {}
    gpg_with_key.sign_package(Path("a"), "a")
    process_mock.assert_not_called()


def test_sign_package_skip_2(gpg_with_key: GPG, mocker: MockerFixture) -> None:
    """
    must not sign package if it is not set
    """
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")
    gpg_with_key.targets = {SignSettings.SignRepository}
    gpg_with_key.sign_package(Path("a"), "a")
    process_mock.assert_not_called()


def test_sign_package_skip_3(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must not sign package if it is not set
    """
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")
    gpg.targets = {SignSettings.SignPackages}
    gpg.sign_package(Path("a"), "a")
    process_mock.assert_not_called()


def test_sign_package_skip_4(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must not sign package if it is not set
    """
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")
    gpg.targets = {SignSettings.SignPackages, SignSettings.SignRepository}
    gpg.sign_package(Path("a"), "a")
    process_mock.assert_not_called()


def test_sign_repository_1(gpg_with_key: GPG, mocker: MockerFixture) -> None:
    """
    must sign repository
    """
    result = [Path("a"), Path("a.sig")]
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process", return_value=result)

    gpg_with_key.targets = {SignSettings.SignRepository}
    assert gpg_with_key.sign_repository(Path("a")) == result
    process_mock.assert_called_once()


def test_sign_repository_2(gpg_with_key: GPG, mocker: MockerFixture) -> None:
    """
    must sign repository
    """
    result = [Path("a"), Path("a.sig")]
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process", return_value=result)

    gpg_with_key.targets = {SignSettings.SignPackages, SignSettings.SignRepository}
    assert gpg_with_key.sign_repository(Path("a")) == result
    process_mock.assert_called_once()


def test_sign_repository_skip_1(gpg_with_key: GPG, mocker: MockerFixture) -> None:
    """
    must not sign repository if it is not set
    """
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")
    gpg_with_key.targets = {}
    gpg_with_key.sign_repository(Path("a"))
    process_mock.assert_not_called()


def test_sign_repository_skip_2(gpg_with_key: GPG, mocker: MockerFixture) -> None:
    """
    must not sign repository if it is not set
    """
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")
    gpg_with_key.targets = {SignSettings.SignPackages}
    gpg_with_key.sign_repository(Path("a"))
    process_mock.assert_not_called()


def test_sign_repository_skip_3(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must not sign repository if it is not set
    """
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")
    gpg.targets = {SignSettings.SignRepository}
    gpg.sign_repository(Path("a"))
    process_mock.assert_not_called()


def test_sign_repository_skip_4(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must not sign repository if it is not set
    """
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")
    gpg.targets = {SignSettings.SignPackages, SignSettings.SignRepository}
    gpg.sign_repository(Path("a"))
    process_mock.assert_not_called()
