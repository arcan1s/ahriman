from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.sign.gpg import GPG
from ahriman.models.sign_settings import SignSettings


def test_repository_sign_args(gpg: GPG) -> None:
    """
    must generate correct sign args
    """
    gpg.target = {SignSettings.SignRepository}
    assert gpg.repository_sign_args


def test_sign_package_1(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must sign package
    """
    result = [Path("a"), Path("a.sig")]
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process", return_value=result)

    gpg.target = {SignSettings.SignPackages}
    assert gpg.sign_package(Path("a"), "a") == result
    process_mock.assert_called_once()


def test_sign_package_2(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must sign package
    """
    result = [Path("a"), Path("a.sig")]
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process", return_value=result)

    gpg.target = {SignSettings.SignPackages, SignSettings.SignRepository}
    assert gpg.sign_package(Path("a"), "a") == result
    process_mock.assert_called_once()


def test_sign_package_skip_1(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must not sign package if it is not set
    """
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")
    gpg.target = {}
    process_mock.assert_not_called()


def test_sign_package_skip_2(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must not sign package if it is not set
    """
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")
    gpg.target = {SignSettings.SignRepository}
    process_mock.assert_not_called()


def test_sign_repository_1(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must sign repository
    """
    result = [Path("a"), Path("a.sig")]
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process", return_value=result)

    gpg.target = {SignSettings.SignRepository}
    assert gpg.sign_repository(Path("a")) == result
    process_mock.assert_called_once()


def test_sign_repository_2(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must sign repository
    """
    result = [Path("a"), Path("a.sig")]
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process", return_value=result)

    gpg.target = {SignSettings.SignPackages, SignSettings.SignRepository}
    assert gpg.sign_repository(Path("a")) == result
    process_mock.assert_called_once()


def test_sign_repository_skip_1(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must not sign repository if it is not set
    """
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")
    gpg.target = {}
    process_mock.assert_not_called()


def test_sign_repository_skip_2(gpg: GPG, mocker: MockerFixture) -> None:
    """
    must not sign repository if it is not set
    """
    process_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process")
    gpg.target = {SignSettings.SignPackages}
    process_mock.assert_not_called()
