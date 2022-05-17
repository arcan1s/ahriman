import datetime
import logging
import pytest
import requests
import subprocess

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.core.exceptions import BuildFailed, InvalidOption, UnsafeRun
from ahriman.core.util import check_output, check_user, exception_response_text, filter_json, full_version, \
    package_like, pretty_datetime, pretty_size, tmpdir, walk
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


def test_check_output(mocker: MockerFixture) -> None:
    """
    must run command and log result
    """
    logger_mock = mocker.patch("logging.Logger.debug")

    assert check_output("echo", "hello", exception=None) == "hello"
    logger_mock.assert_not_called()

    assert check_output("echo", "hello", exception=None, logger=logging.getLogger("")) == "hello"
    logger_mock.assert_called_once_with("hello")


def test_check_output_stderr(mocker: MockerFixture) -> None:
    """
    must run command and log stderr output
    """
    logger_mock = mocker.patch("logging.Logger.debug")

    assert check_output("python", "-c", """import sys; print("hello", file=sys.stderr)""", exception=None) == ""
    logger_mock.assert_not_called()

    assert check_output("python", "-c", """import sys; print("hello", file=sys.stderr)""",
                        exception=None, logger=logging.getLogger("")) == ""
    logger_mock.assert_called_once_with("hello")


def test_check_output_with_stdin() -> None:
    """
    must run command and put string to stdin
    """
    assert check_output("python", "-c", "import sys; value = sys.stdin.read(); print(value)",
                        exception=None, input_data="single line") == "single line"


def test_check_output_with_stdin_newline() -> None:
    """
    must run command and put string to stdin ending with new line
    """
    assert check_output("python", "-c", "import sys; value = sys.stdin.read(); print(value)",
                        exception=None, input_data="single line\n") == "single line"


def test_check_output_multiple_with_stdin() -> None:
    """
    must run command and put multiple lines to stdin
    """
    assert check_output("python", "-c", "import sys; value = sys.stdin.read(); print(value)",
                        exception=None, input_data="multiple\nlines") == "multiple\nlines"


def test_check_output_multiple_with_stdin_newline() -> None:
    """
    must run command and put multiple lines to stdin with new line at the end
    """
    assert check_output("python", "-c", "import sys; value = sys.stdin.read(); print(value)",
                        exception=None, input_data="multiple\nlines\n") == "multiple\nlines"


def test_check_output_failure(mocker: MockerFixture) -> None:
    """
    must process exception correctly
    """
    mocker.patch("subprocess.Popen.wait", return_value=1)

    with pytest.raises(subprocess.CalledProcessError):
        check_output("echo", "hello", exception=None)

    with pytest.raises(subprocess.CalledProcessError):
        check_output("echo", "hello", exception=None, logger=logging.getLogger(""))


def test_check_output_failure_exception(mocker: MockerFixture) -> None:
    """
    must raise exception provided instead of default
    """
    mocker.patch("subprocess.Popen.wait", return_value=1)
    exception = BuildFailed("")

    with pytest.raises(BuildFailed):
        check_output("echo", "hello", exception=exception)

    with pytest.raises(BuildFailed):
        check_output("echo", "hello", exception=exception, logger=logging.getLogger(""))


def test_check_user(mocker: MockerFixture) -> None:
    """
    must check user correctly
    """
    paths = RepositoryPaths(Path.cwd(), "x86_64")
    mocker.patch("os.getuid", return_value=paths.root_owner[0])
    check_user(paths, False)


def test_check_user_no_directory(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must not fail in case if no directory found
    """
    mocker.patch("pathlib.Path.exists", return_value=False)
    check_user(repository_paths, False)


def test_check_user_exception(mocker: MockerFixture) -> None:
    """
    must raise exception if user differs
    """
    paths = RepositoryPaths(Path.cwd(), "x86_64")
    mocker.patch("os.getuid", return_value=paths.root_owner[0] + 1)

    with pytest.raises(UnsafeRun):
        check_user(paths, False)


def test_exception_response_text() -> None:
    """
    must parse HTTP response to string
    """
    response_mock = MagicMock()
    response_mock.text = "hello"
    exception = requests.exceptions.HTTPError(response=response_mock)

    assert exception_response_text(exception) == "hello"


def test_exception_response_text_empty() -> None:
    """
    must parse HTTP exception with empty response to empty string
    """
    exception = requests.exceptions.HTTPError(response=None)
    assert exception_response_text(exception) == ""


def test_check_unsafe(mocker: MockerFixture) -> None:
    """
    must skip check if unsafe flag is set
    """
    paths = RepositoryPaths(Path.cwd(), "x86_64")
    mocker.patch("os.getuid", return_value=paths.root_owner[0] + 1)
    check_user(paths, True)


def test_filter_json(package_ahriman: Package) -> None:
    """
    must filter fields by known list
    """
    expected = package_ahriman.view()
    probe = package_ahriman.view()
    probe["unknown_field"] = "value"

    assert expected == filter_json(probe, expected.keys())


def test_filter_json_empty_value(package_ahriman: Package) -> None:
    """
    must filter empty values from object
    """
    probe = package_ahriman.view()
    probe["base"] = None
    assert "base" not in filter_json(probe, probe.keys())


def test_full_version() -> None:
    """
    must construct full version
    """
    assert full_version("1", "r2388.d30e3201", "1") == "1:r2388.d30e3201-1"
    assert full_version(None, "0.12.1", "1") == "0.12.1-1"
    assert full_version(0, "0.12.1", "1") == "0.12.1-1"
    assert full_version(1, "0.12.1", "1") == "1:0.12.1-1"


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


def test_pretty_datetime_datetime() -> None:
    """
    must generate string from datetime object
    """
    assert pretty_datetime(datetime.datetime(1970, 1, 1, 0, 0, 0)) == "1970-01-01 00:00:00"


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


def test_tmpdir() -> None:
    """
    must create temporary directory and remove it after
    """
    with tmpdir() as directory:
        assert directory.is_dir()
    assert not directory.exists()


def test_tmpdir_failure() -> None:
    """
    must create temporary directory and remove it even after exception
    """
    with pytest.raises(Exception):
        with tmpdir() as directory:
            raise Exception()
    assert not directory.exists()


def test_walk(resource_path_root: Path) -> None:
    """
    must traverse directory recursively
    """
    expected = sorted([
        resource_path_root / "core" / "ahriman.ini",
        resource_path_root / "core" / "logging.ini",
        resource_path_root / "models" / "aur_error",
        resource_path_root / "models" / "big_file_checksum",
        resource_path_root / "models" / "empty_file_checksum",
        resource_path_root / "models" / "official_error",
        resource_path_root / "models" / "package_ahriman_aur",
        resource_path_root / "models" / "package_akonadi_aur",
        resource_path_root / "models" / "package_ahriman_srcinfo",
        resource_path_root / "models" / "package_gcc10_srcinfo",
        resource_path_root / "models" / "package_tpacpi-bat-git_srcinfo",
        resource_path_root / "models" / "package_yay_srcinfo",
        resource_path_root / "web" / "templates" / "build-status" / "login-modal.jinja2",
        resource_path_root / "web" / "templates" / "build-status" / "package-modals.jinja2",
        resource_path_root / "web" / "templates" / "build-status" / "scripts.jinja2",
        resource_path_root / "web" / "templates" / "static" / "favicon.ico",
        resource_path_root / "web" / "templates" / "utils" / "bootstrap-scripts.jinja2",
        resource_path_root / "web" / "templates" / "utils" / "style.jinja2",
        resource_path_root / "web" / "templates" / "build-status.jinja2",
        resource_path_root / "web" / "templates" / "email-index.jinja2",
        resource_path_root / "web" / "templates" / "repo-index.jinja2",
        resource_path_root / "web" / "templates" / "telegram-index.jinja2",
    ])
    local_files = list(sorted(walk(resource_path_root)))
    assert local_files == expected
