import configparser
from io import StringIO

import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import InitializeError
from ahriman.models.repository_id import RepositoryId
from ahriman.models.repository_paths import RepositoryPaths


def test_architecture(configuration: Configuration) -> None:
    """
    must return valid repository architecture
    """
    assert configuration.architecture == "x86_64"


def test_repository_id(configuration: Configuration, repository_id: RepositoryId) -> None:
    """
    must return repository identifier
    """
    assert configuration.repository_id == repository_id
    assert configuration.get("repository", "name") == repository_id.name
    assert configuration.get("repository", "architecture") == repository_id.architecture


def test_repository_id_erase(configuration: Configuration) -> None:
    """
    must remove repository identifier properties if empty identifier supplied
    """
    configuration.repository_id = None
    assert configuration.get("repository", "name", fallback=None) is None
    assert configuration.get("repository", "architecture", fallback=None) is None

    configuration.repository_id = RepositoryId("", "")
    assert configuration.get("repository", "name", fallback=None) is None
    assert configuration.get("repository", "architecture", fallback=None) is None


def test_repository_id_update(configuration: Configuration, repository_id: RepositoryId) -> None:
    """
    must update repository identifier and related configuration options
    """
    repository_id = RepositoryId("i686", repository_id.name)

    configuration.repository_id = repository_id
    assert configuration.repository_id == repository_id
    assert configuration.get("repository", "name") == repository_id.name
    assert configuration.get("repository", "architecture") == repository_id.architecture


def test_repository_name(configuration: Configuration) -> None:
    """
    must return valid repository name
    """
    assert configuration.repository_name == "aur"


def test_repository_paths(configuration: Configuration, repository_paths: RepositoryPaths) -> None:
    """
    must return repository paths
    """
    assert configuration.repository_paths == repository_paths


def test_from_path(repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must load configuration
    """
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("ahriman.core.configuration.Configuration.get", return_value="ahriman.ini.d")
    read_mock = mocker.patch("ahriman.core.configuration.Configuration.read")
    load_includes_mock = mocker.patch("ahriman.core.configuration.Configuration.load_includes")
    path = Path("path")

    configuration = Configuration.from_path(path, repository_id)
    assert configuration.path == path
    read_mock.assert_called_once_with(path)
    load_includes_mock.assert_called_once_with()


def test_from_path_file_missing(repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must load configuration based on package files
    """
    mocker.patch("pathlib.Path.is_file", return_value=False)
    mocker.patch("ahriman.core.configuration.Configuration.load_includes")
    mocker.patch("ahriman.core.configuration.Configuration.get", return_value="ahriman.ini.d")
    read_mock = mocker.patch("ahriman.core.configuration.Configuration.read")

    configuration = Configuration.from_path(Path("path"), repository_id)
    read_mock.assert_called_once_with(configuration.SYSTEM_CONFIGURATION_PATH)


def test_section_name(configuration: Configuration) -> None:
    """
    must return architecture specific group
    """
    assert configuration.section_name("build") == "build"
    assert configuration.section_name("build", None) == "build"
    assert configuration.section_name("build", "x86_64") == "build:x86_64"
    assert configuration.section_name("build", "aur", "x86_64") == "build:aur:x86_64"
    assert configuration.section_name("build", "aur", None) == "build:aur"
    assert configuration.section_name("build", None, "x86_64") == "build:x86_64"


def test_check_loaded(configuration: Configuration) -> None:
    """
    must return valid path and architecture
    """
    path, repository_id = configuration.check_loaded()
    assert path == configuration.path
    assert repository_id == configuration.repository_id


def test_check_loaded_path(configuration: Configuration) -> None:
    """
    must raise exception if path is none
    """
    configuration.path = None
    with pytest.raises(InitializeError):
        configuration.check_loaded()


def test_check_loaded_architecture(configuration: Configuration) -> None:
    """
    must raise exception if architecture is none
    """
    configuration.repository_id = None
    with pytest.raises(InitializeError):
        configuration.check_loaded()


def test_copy_from(configuration: Configuration) -> None:
    """
    must copy values from another instance
    """
    instance = Configuration()
    instance.copy_from(configuration)
    assert instance.dump() == configuration.dump()


def test_dump(configuration: Configuration) -> None:
    """
    dump must not be empty
    """
    assert configuration.dump()


def test_dump_architecture_specific(configuration: Configuration) -> None:
    """
    dump must contain architecture specific settings
    """
    section = configuration.section_name("build", configuration.architecture)
    configuration.set_option(section, "archbuild_flags", "hello flag")
    configuration.merge_sections(configuration.repository_id)

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


def test_getlist_with_spaces(configuration: Configuration) -> None:
    """
    must return list of string if there is string with spaces in quotes
    """
    configuration.set_option("build", "test_list", """"ahriman is" cool""")
    assert configuration.getlist("build", "test_list") == ["""ahriman is""", """cool"""]
    configuration.set_option("build", "test_list", """'ahriman is' cool""")
    assert configuration.getlist("build", "test_list") == ["""ahriman is""", """cool"""]


def test_getlist_with_quotes(configuration: Configuration) -> None:
    """
    must return list of string if there is string with quote inside quote
    """
    configuration.set_option("build", "test_list", """"ahriman is" c"'"ool""")
    assert configuration.getlist("build", "test_list") == ["""ahriman is""", """c'ool"""]
    configuration.set_option("build", "test_list", """'ahriman is' c'"'ool""")
    assert configuration.getlist("build", "test_list") == ["""ahriman is""", """c"ool"""]


def test_getlist_unmatched_quote(configuration: Configuration) -> None:
    """
    must raise exception on unmatched quote in string value
    """
    configuration.set_option("build", "test_list", """ahri"man is cool""")
    with pytest.raises(ValueError):
        configuration.getlist("build", "test_list")
    configuration.set_option("build", "test_list", """ahri'man is cool""")
    with pytest.raises(ValueError):
        configuration.getlist("build", "test_list")


def test_getlist_append() -> None:
    """
    must correctly append list values
    """
    configuration = Configuration()
    configuration._read(
        StringIO("""
        [section]
        list1[] = value1
        list1[] = value2

        list2[] = value3
        list2[] =
        list2[] = value4
        list2[] = value5

        list3[] = value6
        list3 = value7
        list3[] = value8
        """), "io")

    assert configuration.getlist("section", "list1") == ["value1", "value2"]
    assert configuration.getlist("section", "list2") == ["value4", "value5"]
    assert configuration.getlist("section", "list3") == ["value7", "value8"]


def test_getpath_absolute_to_absolute(configuration: Configuration) -> None:
    """
    must not change path for absolute path in settings
    """
    path = Path("/a/b/c")
    configuration.set_option("build", "path", str(path))
    assert configuration.getpath("build", "path") == path


def test_getpath_absolute_to_relative(configuration: Configuration) -> None:
    """
    must prepend root path to relative path
    """
    path = Path("a")
    configuration.set_option("build", "path", str(path))
    result = configuration.getpath("build", "path")
    assert result.is_absolute()
    assert result.parent == configuration.path.parent
    assert result.name == path.name


def test_getpath_with_fallback(configuration: Configuration) -> None:
    """
    must return fallback path
    """
    path = Path("a")
    assert configuration.getpath("some", "option", fallback=path).name == str(path)
    assert configuration.getpath("some", "option", fallback=None) is None


def test_getpath_without_fallback(configuration: Configuration) -> None:
    """
    must raise exception without fallback
    """
    with pytest.raises(configparser.NoSectionError):
        assert configuration.getpath("some", "option")
    with pytest.raises(configparser.NoOptionError):
        assert configuration.getpath("build", "option")


def test_getpathlist(configuration: Configuration) -> None:
    """
    must extract path list
    """
    path = Path("/a/b/c")
    configuration.set_option("build", "path", f"""{path} {path.relative_to("/")}""")

    result = configuration.getpathlist("build", "path")
    assert all(element.is_absolute() for element in result)
    assert path in result
    assert all(element.is_relative_to("/") for element in result)


def test_gettype(configuration: Configuration) -> None:
    """
    must extract type from variable
    """
    section, provider = configuration.gettype("customs3", configuration.repository_id)
    assert section == "customs3"
    assert provider == "s3"


def test_gettype_with_fallback(configuration: Configuration) -> None:
    """
    must return same provider name as in fallback
    """
    section, provider = configuration.gettype("rsync", configuration.repository_id, fallback="abracadabra")
    assert section == "rsync"
    assert provider == "abracadabra"


def test_gettype_from_section(configuration: Configuration) -> None:
    """
    must extract type from section name
    """
    section, provider = configuration.gettype("rsync", configuration.repository_id)
    assert section == "rsync"
    assert provider == "rsync"


def test_gettype_from_section_with_architecture(configuration: Configuration) -> None:
    """
    must extract type from section name with architecture
    """
    section, provider = configuration.gettype("github", configuration.repository_id)
    assert section == "github:x86_64"
    assert provider == "github"


def test_gettype_from_section_no_section(configuration: Configuration) -> None:
    """
    must raise NoSectionError during type extraction from section name with architecture
    """
    # technically rsync:x86_64 is valid section
    # but in current configuration it must be considered as missing section
    with pytest.raises(configparser.NoSectionError):
        configuration.gettype("rsync:x86_64", configuration.repository_id)


def test_load_includes(mocker: MockerFixture) -> None:
    """
    must load includes
    """
    mocker.patch.object(Configuration, "logging_path", Path("logging"))
    read_mock = mocker.patch("ahriman.core.configuration.Configuration.read")
    glob_mock = mocker.patch("pathlib.Path.glob", autospec=True, return_value=[Path("include"), Path("logging")])
    configuration = Configuration()

    configuration.load_includes(Path("path"))
    glob_mock.assert_called_once_with(Path("path"), "*.ini")
    read_mock.assert_called_once_with(Path("include"))
    assert configuration.includes == [Path("include")]


def test_load_includes_missing() -> None:
    """
    must not fail if not include directory found
    """
    configuration = Configuration()
    configuration.set_option("settings", "include", "path")
    configuration.load_includes()


def test_load_includes_no_option() -> None:
    """
    must not fail if no option set
    """
    configuration = Configuration()
    configuration.set_option("settings", "key", "value")
    configuration.load_includes()


def test_load_includes_no_section() -> None:
    """
    must not fail if no section set
    """
    configuration = Configuration()
    configuration.load_includes()


def test_load_includes_default_path(mocker: MockerFixture) -> None:
    """
    must load includes from default path
    """
    mocker.patch.object(Configuration, "include", Path("path"))
    glob_mock = mocker.patch("pathlib.Path.glob", autospec=True, return_value=[])

    Configuration().load_includes()
    glob_mock.assert_called_once_with(Path("path"), "*.ini")


def test_merge_sections_missing(configuration: Configuration) -> None:
    """
    must merge create section if not exists
    """
    section = configuration.section_name("build", configuration.architecture)
    configuration.remove_section("build")
    configuration.set_option(section, "key", "value")

    configuration.merge_sections(configuration.repository_id)
    assert configuration.get("build", "key") == "value"


def test_merge_sections_priority(configuration: Configuration) -> None:
    """
    must merge sections in valid order
    """
    empty = "build"
    arch = configuration.section_name(empty, configuration.architecture)
    repo = configuration.section_name(empty, configuration.repository_name)
    repo_arch = configuration.section_name(empty, configuration.repository_name, configuration.architecture)

    configuration.set_option(empty, "key1", "key1_value1")
    configuration.set_option(arch, "key1", "key1_value2")
    configuration.set_option(repo, "key1", "key1_value3")
    configuration.set_option(repo_arch, "key1", "key1_value4")

    configuration.set_option(empty, "key2", "key2_value1")
    configuration.set_option(arch, "key2", "key2_value2")
    configuration.set_option(repo, "key2", "key2_value3")

    configuration.set_option(empty, "key3", "key3_value1")
    configuration.set_option(arch, "key3", "key3_value2")

    configuration.set_option(empty, "key4", "key4_value1")

    configuration.merge_sections(configuration.repository_id)
    assert configuration.get("build", "key1") == "key1_value4"
    assert configuration.get("build", "key2") == "key2_value3"
    assert configuration.get("build", "key3") == "key3_value2"
    assert configuration.get("build", "key4") == "key4_value1"


def test_override_sections(configuration: Configuration, repository_id: RepositoryId) -> None:
    """
    must correctly generate override section names
    """
    assert configuration.override_sections("build", repository_id) == [
        "build:x86_64",
        "build:aur",
        "build:aur:x86_64",
    ]


def test_override_sections_empty(configuration: Configuration) -> None:
    """
    must look up for sections if repository identifier is empty
    """
    configuration.set_option("web:x86_64", "port", "8080")
    configuration.set_option("web:i686", "port", "8080")
    assert configuration.override_sections("web", RepositoryId("", "")) == ["web:i686", "web:x86_64"]


def test_reload(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must reload configuration
    """
    load_mock = mocker.patch("ahriman.core.configuration.Configuration.load")
    merge_mock = mocker.patch("ahriman.core.configuration.Configuration.merge_sections")

    configuration.reload()
    load_mock.assert_called_once_with(configuration.path)
    merge_mock.assert_called_once_with(configuration.repository_id)


def test_reload_clear(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must clear current settings before configuration reload
    """
    clear_mock = mocker.patch("ahriman.core.configuration.Configuration.remove_section")
    sections = configuration.sections()

    configuration.reload()
    clear_mock.assert_has_calls([MockCall(section) for section in sections])


def test_reload_no_architecture(configuration: Configuration) -> None:
    """
    must raise exception on reload if no architecture set
    """
    configuration.repository_id = None
    with pytest.raises(InitializeError):
        configuration.reload()


def test_reload_no_path(configuration: Configuration) -> None:
    """
    must raise exception on reload if no path set
    """
    configuration.path = None
    with pytest.raises(InitializeError):
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
