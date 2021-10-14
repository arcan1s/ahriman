import configparser
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import InitializeException


def test_from_path(mocker: MockerFixture) -> None:
    """
    must load configuration
    """
    read_mock = mocker.patch("ahriman.core.configuration.Configuration.read")
    load_includes_mock = mocker.patch("ahriman.core.configuration.Configuration.load_includes")
    load_logging_mock = mocker.patch("ahriman.core.configuration.Configuration.load_logging")
    path = Path("path")

    configuration = Configuration.from_path(path, "x86_64", True)
    assert configuration.path == path
    read_mock.assert_called_once_with(path)
    load_includes_mock.assert_called_once()
    load_logging_mock.assert_called_once()


def test_section_name(configuration: Configuration) -> None:
    """
    must return architecture specific group
    """
    assert configuration.section_name("build", "x86_64") == "build:x86_64"


def test_absolute_path_for_absolute(configuration: Configuration) -> None:
    """
    must not change path for absolute path in settings
    """
    path = Path("/a/b/c")
    configuration.set_option("build", "path", str(path))
    assert configuration.getpath("build", "path") == path


def test_absolute_path_for_relative(configuration: Configuration) -> None:
    """
    must prepend root path to relative path
    """
    path = Path("a")
    configuration.set_option("build", "path", str(path))
    result = configuration.getpath("build", "path")
    assert result.is_absolute()
    assert result.parent == configuration.path.parent
    assert result.name == path.name


def test_path_with_fallback(configuration: Configuration) -> None:
    """
    must return fallback path
    """
    path = Path("a")
    assert configuration.getpath("some", "option", fallback=path).name == str(path)
    assert configuration.getpath("some", "option", fallback=None) is None


def test_path_without_fallback(configuration: Configuration) -> None:
    """
    must raise exception without fallback
    """
    with pytest.raises(configparser.NoSectionError):
        assert configuration.getpath("some", "option")
    with pytest.raises(configparser.NoOptionError):
        assert configuration.getpath("build", "option")


def test_dump(configuration: Configuration) -> None:
    """
    dump must not be empty
    """
    assert configuration.dump()


def test_dump_architecture_specific(configuration: Configuration) -> None:
    """
    dump must contain architecture specific settings
    """
    section = configuration.section_name("build", "x86_64")
    configuration.set_option(section, "archbuild_flags", "hello flag")
    configuration.merge_sections("x86_64")

    dump = configuration.dump()
    assert dump
    assert "build" in dump
    assert section not in dump
    assert dump["build"]["archbuild_flags"] == "hello flag"


def test_getlist(configuration: Configuration) -> None:
    """
    must return list of string correctly
    """
    configuration.set_option("build", "test_list", "a b c")
    assert configuration.getlist("build", "test_list") == ["a", "b", "c"]


def test_getlist_empty(configuration: Configuration) -> None:
    """
    must return list of string correctly for non-existing option
    """
    assert configuration.getlist("build", "test_list", fallback=[]) == []
    configuration.set_option("build", "test_list", "")
    assert configuration.getlist("build", "test_list") == []


def test_getlist_single(configuration: Configuration) -> None:
    """
    must return list of strings for single string
    """
    configuration.set_option("build", "test_list", "a")
    assert configuration.getlist("build", "test_list") == ["a"]
    assert configuration.getlist("build", "test_list") == ["a"]


def test_load_includes_missing(configuration: Configuration) -> None:
    """
    must not fail if not include directory found
    """
    configuration.set_option("settings", "include", "path")
    configuration.load_includes()


def test_load_includes_no_option(configuration: Configuration) -> None:
    """
    must not fail if no option set
    """
    configuration.remove_option("settings", "include")
    configuration.load_includes()


def test_load_includes_no_section(configuration: Configuration) -> None:
    """
    must not fail if no option set
    """
    configuration.remove_section("settings")
    configuration.load_includes()


def test_load_logging_fallback(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must fallback to stderr without errors
    """
    mocker.patch("logging.config.fileConfig", side_effect=PermissionError())
    configuration.load_logging(quiet=False)


def test_load_logging_quiet(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must disable logging in case if quiet flag set
    """
    disable_mock = mocker.patch("logging.disable")
    configuration.load_logging(quiet=True)
    disable_mock.assert_called_once()


def test_merge_sections_missing(configuration: Configuration) -> None:
    """
    must merge create section if not exists
    """
    section = configuration.section_name("build", "x86_64")
    configuration.remove_section("build")
    configuration.set_option(section, "key", "value")

    configuration.merge_sections("x86_64")
    assert configuration.get("build", "key") == "value"


def test_reload(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must reload configuration
    """
    load_mock = mocker.patch("ahriman.core.configuration.Configuration.load")
    merge_mock = mocker.patch("ahriman.core.configuration.Configuration.merge_sections")

    configuration.reload()
    load_mock.assert_called_once()
    merge_mock.assert_called_once()


def test_reload_no_architecture(configuration: Configuration) -> None:
    """
    must raise exception on reload if no architecture set
    """
    configuration.architecture = None
    with pytest.raises(InitializeException):
        configuration.reload()


def test_reload_no_path(configuration: Configuration) -> None:
    """
    must raise exception on reload if no path set
    """
    configuration.path = None
    with pytest.raises(InitializeException):
        configuration.reload()


def test_set_option(configuration: Configuration) -> None:
    """
    must set option correctly
    """
    configuration.set_option("settings", "option", "value")
    assert configuration.get("settings", "option") == "value"


def test_set_option_new_section(configuration: Configuration) -> None:
    """
    must set option correctly even if no section found
    """
    configuration.set_option("section", "option", "value")
    assert configuration.get("section", "option") == "value"
