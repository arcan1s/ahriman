from pathlib import Path

from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration


def test_from_path(mocker: MockerFixture) -> None:
    """
    must load configuration
    """
    read_mock = mocker.patch("configparser.RawConfigParser.read")
    load_includes_mock = mocker.patch("ahriman.core.configuration.Configuration.load_includes")
    load_logging_mock = mocker.patch("ahriman.core.configuration.Configuration.load_logging")
    path = Path("path")

    config = Configuration.from_path(path, True)
    assert config.path == path
    read_mock.assert_called_with(path)
    load_includes_mock.assert_called_once()
    load_logging_mock.assert_called_once()


def test_absolute_path_for_absolute(configuration: Configuration) -> None:
    """
    must not change path for absolute path in settings
    """
    path = Path("/a/b/c")
    assert configuration.absolute_path_for(path) == path


def test_absolute_path_for_relative(configuration: Configuration) -> None:
    """
    must prepend root path to relative path
    """
    path = Path("a")
    result = configuration.absolute_path_for(path)
    assert result.is_absolute()
    assert result.parent == configuration.path.parent
    assert result.name == path.name


def test_dump(configuration: Configuration) -> None:
    """
    dump must not be empty
    """
    assert configuration.dump("x86_64")


def test_dump_architecture_specific(configuration: Configuration) -> None:
    """
    dump must contain architecture specific settings
    """
    configuration.add_section("build_x86_64")
    configuration.set("build_x86_64", "archbuild_flags", "")

    dump = configuration.dump("x86_64")
    assert dump
    assert "build" not in dump
    assert "build_x86_64" in dump


def test_getlist(configuration: Configuration) -> None:
    """
    must return list of string correctly
    """
    configuration.set("build", "test_list", "a b c")
    assert configuration.getlist("build", "test_list") == ["a", "b", "c"]


def test_getlist_empty(configuration: Configuration) -> None:
    """
    must return list of string correctly for non-existing option
    """
    assert configuration.getlist("build", "test_list") == []
    configuration.set("build", "test_list", "")
    assert configuration.getlist("build", "test_list") == []


def test_getlist_single(configuration: Configuration) -> None:
    """
    must return list of strings for single string
    """
    configuration.set("build", "test_list", "a")
    assert configuration.getlist("build", "test_list") == ["a"]


def test_get_section_name(configuration: Configuration) -> None:
    """
    must return architecture specific group
    """
    configuration.add_section("build_x86_64")
    configuration.set("build_x86_64", "archbuild_flags", "")
    assert configuration.get_section_name("build", "x86_64") == "build_x86_64"


def test_get_section_name_missing(configuration: Configuration) -> None:
    """
    must return default group if architecture depending group does not exist
    """
    assert configuration.get_section_name("prefix", "suffix") == "prefix"
    assert configuration.get_section_name("build", "x86_64") == "build"


def test_load_includes_missing(configuration: Configuration) -> None:
    """
    must not fail if not include directory found
    """
    configuration.set("settings", "include", "path")
    configuration.load_includes()


def test_load_logging_fallback(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must fallback to stderr without errors
    """
    mocker.patch("logging.config.fileConfig", side_effect=PermissionError())
    configuration.load_logging(True)


def test_load_logging_stderr(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must use stderr if flag set
    """
    logging_mock = mocker.patch("logging.config.fileConfig")
    configuration.load_logging(False)
    logging_mock.assert_not_called()
