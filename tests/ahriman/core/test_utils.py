import datetime
import fcntl
import logging
import os
import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from typing import Any
from unittest.mock import MagicMock, call as MockCall

from ahriman.core.exceptions import BuildError, CalledProcessError, OptionError, UnsafeRunError
from ahriman.core.utils import *
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource
from ahriman.models.repository_id import RepositoryId
from ahriman.models.repository_paths import RepositoryPaths


def test_atomic_move(mocker: MockerFixture) -> None:
    """
    must move file with locking
    """
    lock_mock = mocker.patch("fcntl.flock")
    open_mock = mocker.patch("pathlib.Path.open", autospec=True)
    move_mock = mocker.patch("shutil.move")
    unlink_mock = mocker.patch("pathlib.Path.unlink")

    atomic_move(Path("source"), Path("destination"))
    open_mock.assert_called_once_with(Path(".destination"), "ab")
    lock_mock.assert_has_calls([
        MockCall(pytest.helpers.anyvar(int), fcntl.LOCK_EX),
        MockCall(pytest.helpers.anyvar(int), fcntl.LOCK_UN),
    ])
    move_mock.assert_called_once_with(Path("source"), Path("destination"))
    unlink_mock.assert_called_once_with(missing_ok=True)


def test_atomic_move_remove_lock(mocker: MockerFixture) -> None:
    """
    must remove lock file in case of exception
    """
    mocker.patch("pathlib.Path.open", side_effect=Exception)
    unlink_mock = mocker.patch("pathlib.Path.unlink")

    with pytest.raises(Exception):
        atomic_move(Path("source"), Path("destination"))
    unlink_mock.assert_called_once_with(missing_ok=True)


def test_atomic_move_unlock(mocker: MockerFixture) -> None:
    """
    must unlock file in case of exception
    """
    mocker.patch("pathlib.Path.open")
    mocker.patch("shutil.move", side_effect=Exception)
    lock_mock = mocker.patch("fcntl.flock")

    with pytest.raises(Exception):
        atomic_move(Path("source"), Path("destination"))
    lock_mock.assert_has_calls([
        MockCall(pytest.helpers.anyvar(int), fcntl.LOCK_EX),
        MockCall(pytest.helpers.anyvar(int), fcntl.LOCK_UN),
    ])


def test_check_output(mocker: MockerFixture) -> None:
    """
    must run command and log result
    """
    logger_mock = mocker.patch("logging.Logger.debug")

    assert check_output("echo", "hello") == "hello"
    logger_mock.assert_not_called()

    assert check_output("echo", "hello", logger=logging.getLogger("")) == "hello"
    logger_mock.assert_called_once_with("hello")


def test_check_output_stderr(mocker: MockerFixture) -> None:
    """
    must run command and log stderr output
    """
    logger_mock = mocker.patch("logging.Logger.debug")

    assert check_output("python", "-c", """import sys; print("hello", file=sys.stderr)""") == ""
    logger_mock.assert_not_called()

    assert check_output("python", "-c", """import sys; print("hello", file=sys.stderr)""",
                        logger=logging.getLogger("")) == ""
    logger_mock.assert_called_once_with("hello")


def test_check_output_with_stdin() -> None:
    """
    must run command and put string to stdin
    """
    assert check_output("python", "-c", "import sys; value = sys.stdin.read(); print(value)",
                        input_data="single line") == "single line"


def test_check_output_with_stdin_newline() -> None:
    """
    must run command and put string to stdin ending with new line
    """
    assert check_output("python", "-c", "import sys; value = sys.stdin.read(); print(value)",
                        input_data="single line\n") == "single line"


def test_check_output_multiple_with_stdin() -> None:
    """
    must run command and put multiple lines to stdin
    """
    assert check_output("python", "-c", "import sys; value = sys.stdin.read(); print(value)",
                        input_data="multiple\nlines") == "multiple\nlines"


def test_check_output_multiple_with_stdin_newline() -> None:
    """
    must run command and put multiple lines to stdin with new line at the end
    """
    assert check_output("python", "-c", "import sys; value = sys.stdin.read(); print(value)",
                        input_data="multiple\nlines\n") == "multiple\nlines"


def test_check_output_with_user(passwd: Any, mocker: MockerFixture) -> None:
    """
    must run command as specified user and set its homedir
    """
    assert check_output("python", "-c", """import os; print(os.getenv("HOME"))""") != passwd.pw_dir

    getpwuid_mock = mocker.patch("ahriman.core.utils.getpwuid", return_value=passwd)
    user = os.getuid()

    assert check_output("python", "-c", """import os; print(os.getenv("HOME"))""", user=user) == passwd.pw_dir
    getpwuid_mock.assert_called_once_with(user)


def test_check_output_with_user_and_environment(passwd: Any, mocker: MockerFixture) -> None:
    """
    must run set environment if both environment and user are set
    """
    mocker.patch("ahriman.core.utils.getpwuid", return_value=passwd)
    user = os.getuid()
    assert check_output("python", "-c", """import os; print(os.getenv("HOME"), os.getenv("VAR"))""",
                        environment={"VAR": "VALUE"}, user=user) == f"{passwd.pw_dir} VALUE"


def test_check_output_failure(mocker: MockerFixture) -> None:
    """
    must process exception correctly
    """
    mocker.patch("subprocess.Popen.wait", return_value=1)

    with pytest.raises(CalledProcessError):
        check_output("echo", "hello")

    with pytest.raises(CalledProcessError):
        check_output("echo", "hello", logger=logging.getLogger(""))


def test_check_output_failure_exception(mocker: MockerFixture) -> None:
    """
    must raise exception provided instead of default
    """
    mocker.patch("subprocess.Popen.wait", return_value=1)
    exception = BuildError("")

    with pytest.raises(BuildError):
        check_output("echo", "hello", exception=exception)

    with pytest.raises(BuildError):
        check_output("echo", "hello", exception=exception, logger=logging.getLogger(""))


def test_check_output_failure_exception_callable(mocker: MockerFixture) -> None:
    """
    must raise exception from callable provided instead of default
    """
    mocker.patch("subprocess.Popen.wait", return_value=1)
    exception = BuildError.from_process("")

    with pytest.raises(BuildError):
        check_output("echo", "hello", exception=exception)

    with pytest.raises(BuildError):
        check_output("echo", "hello", exception=exception, logger=logging.getLogger(""))


def test_check_output_empty_line(mocker: MockerFixture) -> None:
    """
    must correctly process empty lines in command output
    """
    logger_mock = mocker.patch("logging.Logger.debug")
    assert check_output("python", "-c", """print(); print("hello")""", logger=logging.getLogger("")) == "\nhello"
    logger_mock.assert_has_calls([MockCall(""), MockCall("hello")])


def test_check_output_encoding_error(resource_path_root: Path) -> None:
    """
    must correctly process unicode encoding error in command output
    """
    assert check_output("cat", str(resource_path_root / "models" / "package_pacman-static_pkgbuild"))


def test_check_user(repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must check user correctly
    """
    paths = RepositoryPaths(Path.cwd(), repository_id)
    mocker.patch("os.geteuid", return_value=paths.root_owner[0])
    check_user(paths.root, unsafe=False)


def test_check_user_no_directory(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must not fail in case if no directory found
    """
    mocker.patch("pathlib.Path.exists", return_value=False)
    check_user(repository_paths.root, unsafe=False)


def test_check_user_exception(repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must raise exception if user differs
    """
    paths = RepositoryPaths(Path.cwd(), repository_id)
    mocker.patch("os.geteuid", return_value=paths.root_owner[0] + 1)

    with pytest.raises(UnsafeRunError):
        check_user(paths.root, unsafe=False)


def test_check_user_unsafe(repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must skip check if unsafe flag is set
    """
    paths = RepositoryPaths(Path.cwd(), repository_id)
    mocker.patch("os.geteuid", return_value=paths.root_owner[0] + 1)
    check_user(paths.root, unsafe=True)


def test_dataclass_view(package_ahriman: Package) -> None:
    """
    must serialize dataclasses
    """
    assert Package.from_json(dataclass_view(package_ahriman)) == package_ahriman


def test_dataclass_view_without_none(package_ahriman: Package) -> None:
    """
    must serialize dataclasses with None fields removed
    """
    package_ahriman.packager = None
    result = dataclass_view(package_ahriman)
    assert "packager" not in result
    assert Package.from_json(result) == package_ahriman


def test_enum_values() -> None:
    """
    must correctly generate choices from enumeration classes
    """
    values = enum_values(PackageSource)
    for value in values:
        assert PackageSource(value).value == value


def test_extract_user() -> None:
    """
    must extract user from system environment
    """
    os.environ["USER"] = "user"
    assert extract_user() == "user"

    os.environ["SUDO_USER"] = "sudo"
    assert extract_user() == "sudo"

    os.environ["DOAS_USER"] = "doas"
    assert extract_user() == "sudo"

    del os.environ["SUDO_USER"]
    assert extract_user() == "doas"


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


def test_list_flatmap() -> None:
    """
    must flat map iterable correctly
    """
    assert list_flatmap([], lambda e: [e * 2]) == []
    assert list_flatmap([3, 1, 2], lambda e: [e * 2]) == [2, 4, 6]
    assert list_flatmap([1, 2, 1], lambda e: [e * 2]) == [2, 4]


def test_minmax() -> None:
    """
    must correctly define minimal and maximal value
    """
    assert minmax([1, 4, 3, 2]) == (1, 4)
    assert minmax([[1, 2, 3], [4, 5], [6, 7, 8, 9]], key=len) == ([4, 5], [6, 7, 8, 9])


def test_owner(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must correctly retrieve owner of the path
    """
    stat_mock = MagicMock()
    stat_mock.st_uid = 42
    stat_mock.st_gid = 142
    mocker.patch("pathlib.Path.stat", return_value=stat_mock)

    assert owner(repository_paths.root) == (42, 142)


def test_package_like(package_ahriman: Package) -> None:
    """
    package_like must return true for archives
    """
    assert package_like(package_ahriman.packages[package_ahriman.base].filepath)


def test_package_like_hidden(package_ahriman: Package) -> None:
    """
    package_like must return false for hidden files
    """
    package_file = package_ahriman.packages[package_ahriman.base].filepath
    hidden_file = package_file.parent / f".{package_file.name}"
    assert not package_like(hidden_file)


def test_package_like_sig(package_ahriman: Package) -> None:
    """
    package_like must return false for signature files
    """
    package_file = package_ahriman.packages[package_ahriman.base].filepath
    sig_file = package_file.parent / f"{package_file.name}.sig"
    assert not package_like(sig_file)


def test_parse_version() -> None:
    """
    must correctly parse version into components
    """
    assert parse_version("1.2.3-4") == (None, "1.2.3", "4")
    assert parse_version("5:1.2.3-4") == ("5", "1.2.3", "4")
    assert parse_version("1.2.3-4.2") == (None, "1.2.3", "4.2")
    assert parse_version("0:1.2.3-4.2") == ("0", "1.2.3", "4.2")
    assert parse_version("0:1.2.3-4") == ("0", "1.2.3", "4")


def test_partition() -> None:
    """
    must partition list based on predicate
    """
    even, odd = partition([1, 4, 2, 1, 3, 4], lambda i: i % 2 == 0)
    assert even == [4, 2, 4]
    assert odd == [1, 1, 3]


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


def test_pretty_interval() -> None:
    """
    must generate string from interval
    """
    assert pretty_interval(1) == "1 second"
    assert pretty_interval(42) == "42 seconds"
    assert pretty_interval(62) == "1 minute 2 seconds"
    assert pretty_interval(121) == "2 minutes 1 second"
    assert pretty_interval(3600) == "1 hour"
    assert pretty_interval(7242) == "2 hours 42 seconds"


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
    with pytest.raises(OptionError):
        pretty_size(42 * 1024 * 1024 * 1024 * 1024, 4).split()


def test_pretty_size_empty() -> None:
    """
    must generate empty string for None value
    """
    assert pretty_size(None) == ""


def test_safe_filename() -> None:
    """
    must replace unsafe characters by dashes
    """
    # so far I found only plus sign
    assert safe_filename(
        "gconf-3.2.6+11+g07808097-10-x86_64.pkg.tar.zst") == "gconf-3.2.6-11-g07808097-10-x86_64.pkg.tar.zst"
    assert safe_filename(
        "netkit-telnet-ssl-0.17.41+0.2-6-x86_64.pkg.tar.zst") == "netkit-telnet-ssl-0.17.41-0.2-6-x86_64.pkg.tar.zst"
    assert safe_filename("spotify-1:1.1.84.716-2-x86_64.pkg.tar.zst") == "spotify-1:1.1.84.716-2-x86_64.pkg.tar.zst"
    assert safe_filename("tolua++-1.0.93-4-x86_64.pkg.tar.zst") == "tolua---1.0.93-4-x86_64.pkg.tar.zst"


def test_srcinfo_property() -> None:
    """
    must correctly extract properties
    """
    assert srcinfo_property("key", {"key": "root"}, {"key": "overrides"}, default="default") == "overrides"
    assert srcinfo_property("key", {"key": "root"}, {}, default="default") == "root"
    assert srcinfo_property("key", {}, {"key": "overrides"}, default="default") == "overrides"
    assert srcinfo_property("key", {}, {}, default="default") == "default"
    assert srcinfo_property("key", {}, {}) is None


def test_srcinfo_property_list() -> None:
    """
    must correctly extract property list
    """
    assert srcinfo_property_list("key", {"key": ["root"]}, {"key": ["overrides"]}) == ["overrides"]
    assert srcinfo_property_list("key", {"key": ["root"]}, {"key_x86_64": ["overrides"]}, architecture="x86_64") == [
        "root", "overrides"
    ]
    assert srcinfo_property_list("key", {"key": ["root"], "key_x86_64": ["overrides"]}, {}, architecture="x86_64") == [
        "root", "overrides"
    ]
    assert srcinfo_property_list("key", {"key_x86_64": ["overrides"]}, {}, architecture="x86_64") == ["overrides"]


def test_trim_package() -> None:
    """
    must trim package version
    """
    assert trim_package("package=1") == "package"
    assert trim_package("package>=1") == "package"
    assert trim_package("package>1") == "package"
    assert trim_package("package<1") == "package"
    assert trim_package("package<=1") == "package"
    assert trim_package("package: a description") == "package"


def test_utcnow() -> None:
    """
    must generate correct timestamp
    """
    ts1 = utcnow()
    ts2 = utcnow()
    assert 1 > (ts2 - ts1).total_seconds() > 0


def test_walk(resource_path_root: Path) -> None:
    """
    must traverse directory recursively
    """
    expected = sorted([
        resource_path_root / "core" / "ahriman.ini",
        resource_path_root / "core" / "arcanisrepo.files.tar.gz",
        resource_path_root / "core" / "logging.ini",
        resource_path_root / "models" / "aur_error",
        resource_path_root / "models" / "big_file_checksum",
        resource_path_root / "models" / "empty_file_checksum",
        resource_path_root / "models" / "official_error",
        resource_path_root / "models" / "package_ahriman_aur",
        resource_path_root / "models" / "package_akonadi_aur",
        resource_path_root / "models" / "package_ahriman_files",
        resource_path_root / "models" / "package_ahriman_pkgbuild",
        resource_path_root / "models" / "package_gcc10_pkgbuild",
        resource_path_root / "models" / "package_jellyfin-ffmpeg6-bin_pkgbuild",
        resource_path_root / "models" / "package_pacman-static_pkgbuild",
        resource_path_root / "models" / "package_python-pytest-loop_pkgbuild",
        resource_path_root / "models" / "package_tpacpi-bat-git_pkgbuild",
        resource_path_root / "models" / "package_vim-youcompleteme-git_pkgbuild",
        resource_path_root / "models" / "package_yay_pkgbuild",
        resource_path_root / "models" / "pkgbuild",
        resource_path_root / "models" / "utf8",
        resource_path_root / "web" / "templates" / "build-status" / "alerts.jinja2",
        resource_path_root / "web" / "templates" / "build-status" / "dashboard.jinja2",
        resource_path_root / "web" / "templates" / "build-status" / "key-import-modal.jinja2",
        resource_path_root / "web" / "templates" / "build-status" / "login-modal.jinja2",
        resource_path_root / "web" / "templates" / "build-status" / "package-add-modal.jinja2",
        resource_path_root / "web" / "templates" / "build-status" / "package-info-modal.jinja2",
        resource_path_root / "web" / "templates" / "build-status" / "package-rebuild-modal.jinja2",
        resource_path_root / "web" / "templates" / "build-status" / "table.jinja2",
        resource_path_root / "web" / "templates" / "static" / "favicon.ico",
        resource_path_root / "web" / "templates" / "static" / "logo.svg",
        resource_path_root / "web" / "templates" / "utils" / "bootstrap-scripts.jinja2",
        resource_path_root / "web" / "templates" / "utils" / "style.jinja2",
        resource_path_root / "web" / "templates" / "api.jinja2",
        resource_path_root / "web" / "templates" / "build-status.jinja2",
        resource_path_root / "web" / "templates" / "email-index.jinja2",
        resource_path_root / "web" / "templates" / "error.jinja2",
        resource_path_root / "web" / "templates" / "repo-index.jinja2",
        resource_path_root / "web" / "templates" / "rss.jinja2",
        resource_path_root / "web" / "templates" / "shell",
        resource_path_root / "web" / "templates" / "telegram-index.jinja2",
    ])
    local_files = list(sorted(walk(resource_path_root)))
    assert local_files == expected
