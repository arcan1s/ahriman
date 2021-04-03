import logging
import pytest
import subprocess

from pytest_mock import MockerFixture

from ahriman.core.exceptions import InvalidOption
from ahriman.core.util import check_output, package_like, pretty_datetime, pretty_size
from ahriman.models.package import Package


def test_check_output(mocker: MockerFixture) -> None:
    """
    must run command and log result
    """
    logger_mock = mocker.patch("logging.Logger.debug")

    assert check_output("echo", "hello", exception=None) == "hello"
    logger_mock.assert_not_called()

    assert check_output("echo", "hello", exception=None, logger=logging.getLogger("")) == "hello"
    logger_mock.assert_called_once()


def test_check_output_failure(mocker: MockerFixture) -> None:
    """
    must process exception correctly
    """
    logger_mock = mocker.patch("logging.Logger.debug")
    mocker.patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "echo"))

    with pytest.raises(subprocess.CalledProcessError):
        check_output("echo", "hello", exception=None)
        logger_mock.assert_not_called()

    with pytest.raises(subprocess.CalledProcessError):
        check_output("echo", "hello", exception=None, logger=logging.getLogger(""))
        logger_mock.assert_not_called()


def test_check_output_failure_log(mocker: MockerFixture) -> None:
    """
    must process exception correctly and log it
    """
    logger_mock = mocker.patch("logging.Logger.debug")
    mocker.patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "echo", output=b"result"))

    with pytest.raises(subprocess.CalledProcessError):
        check_output("echo", "hello", exception=None, logger=logging.getLogger(""))
        logger_mock.assert_called_once()


def test_package_like(package_ahriman: Package) -> None:
    """
    package_like must return true for archives
    """
    assert package_like(package_ahriman.packages[package_ahriman.base].filepath)


def test_package_like_sig(package_ahriman: Package) -> None:
    """
    package_like must return false for signature files
    """
    package_file = package_ahriman.packages[package_ahriman.base].filepath
    sig_file = package_file.parent / f"{package_file.name}.sig"
    assert not package_like(sig_file)


def test_pretty_datetime() -> None:
    """
    must generate string from timestamp value
    """
    assert pretty_datetime(0) == "1970-01-01 00:00:00"


def test_pretty_datetime_empty() -> None:
    """
    must generate empty string from None timestamp
    """
    assert pretty_datetime(None) == ""


def test_pretty_size_bytes() -> None:
    """
    must generate bytes string for bytes value
    """
    value, abbrev = pretty_size(42).split()
    assert value == "42.0"
    assert abbrev == "B"


def test_pretty_size_kbytes() -> None:
    """
    must generate kibibytes string for kibibytes value
    """
    value, abbrev = pretty_size(42 * 1024).split()
    assert value == "42.0"
    assert abbrev == "KiB"


def test_pretty_size_mbytes() -> None:
    """
    must generate mebibytes string for mebibytes value
    """
    value, abbrev = pretty_size(42 * 1024 * 1024).split()
    assert value == "42.0"
    assert abbrev == "MiB"


def test_pretty_size_gbytes() -> None:
    """
    must generate gibibytes string for gibibytes value
    """
    value, abbrev = pretty_size(42 * 1024 * 1024 * 1024).split()
    assert value == "42.0"
    assert abbrev == "GiB"


def test_pretty_size_pbytes() -> None:
    """
    must generate pebibytes string for pebibytes value
    """
    value, abbrev = pretty_size(42 * 1024 * 1024 * 1024 * 1024).split()
    assert value == "43008.0"
    assert abbrev == "GiB"


def test_pretty_size_pbytes_failure() -> None:
    """
    must raise exception if level >= 4 supplied
    """
    with pytest.raises(InvalidOption):
        pretty_size(42 * 1024 * 1024 * 1024 * 1024, 4).split()


def test_pretty_size_empty() -> None:
    """
    must generate empty string for None value
    """
    assert pretty_size(None) == ""
