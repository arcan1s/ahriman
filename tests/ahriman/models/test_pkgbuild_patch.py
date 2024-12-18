import json
import pytest
import shlex

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import MagicMock, call

from ahriman.models.pkgbuild_patch import PkgbuildPatch


def test_post_init() -> None:
    """
    must remove empty keys
    """
    assert PkgbuildPatch("", "value").key is None
    assert PkgbuildPatch(None, "value").key is None
    assert PkgbuildPatch("key", "value").key == "key"


def test_is_function() -> None:
    """
    must correctly define key as function
    """
    assert not PkgbuildPatch("key", "value").is_function
    assert PkgbuildPatch("key()", "value").is_function


def test_is_plain_diff() -> None:
    """
    must correctly define key as a plain diff
    """
    assert not PkgbuildPatch("key", "value").is_plain_diff
    assert PkgbuildPatch(None, "value").is_plain_diff


def test_from_env() -> None:
    """
    must construct patch from environment variable
    """
    assert PkgbuildPatch.from_env("KEY=VALUE") == PkgbuildPatch("KEY", "VALUE")
    assert PkgbuildPatch.from_env("KEY=VA=LUE") == PkgbuildPatch("KEY", "VA=LUE")
    assert PkgbuildPatch.from_env("KEY=") == PkgbuildPatch("KEY", "")
    assert PkgbuildPatch.from_env("KEY") == PkgbuildPatch("KEY", "")


def test_from_json_view() -> None:
    """
    must correctly serialize to json
    """
    patch = PkgbuildPatch("key", "value")
    assert PkgbuildPatch.from_json(patch.view()) == patch


def test_parse() -> None:
    """
    must parse string correctly
    """
    assert PkgbuildPatch.parse("key", "VALUE").value == "VALUE"
    assert PkgbuildPatch.parse("key", "(ARRAY VALUE)").value == ["ARRAY", "VALUE"]
    assert PkgbuildPatch.parse("key", """("QU'OUTED" ARRAY VALUE)""").value == ["QU'OUTED", "ARRAY", "VALUE"]
    assert PkgbuildPatch.parse("key()", """{ function with " quotes }""").value == """{ function with " quotes }"""
    assert PkgbuildPatch.parse("key", json.dumps(["array", "value"])).value == ["array", "value"]
    assert PkgbuildPatch.parse("key", ["array", "value"]).value == ["array", "value"]


def test_quote() -> None:
    """
    must quote strings if unsafe flag is not set
    """
    assert PkgbuildPatch.quote("value") == """value"""
    assert PkgbuildPatch.quote("va'lue") == """'va'"'"'lue'"""
    assert PkgbuildPatch.quote("https://github.com/arcan1s/ahriman/releases/download/$pkgver/$pkgbase-$pkgver.tar.gz") == \
        """\"https://github.com/arcan1s/ahriman/releases/download/$pkgver/$pkgbase-$pkgver.tar.gz\""""


def test_unquote() -> None:
    """
    must remove quotation marks
    """
    for source in (
        "abc",
        "ab'c",
        "ab\"c",
    ):
        assert PkgbuildPatch.unquote(shlex.quote(source)) == source


def test_unquote_error() -> None:
    """
    must raise value error on invalid quotation
    """
    with pytest.raises(ValueError):
        PkgbuildPatch.unquote("ab'c")


def test_serialize() -> None:
    """
    must correctly serialize string values
    """
    assert PkgbuildPatch("key", "value").serialize() == "key=value"
    assert PkgbuildPatch("key", "42").serialize() == "key=42"
    assert PkgbuildPatch("key", "4'2").serialize() == """key='4'"'"'2'"""


def test_from_env_serialize() -> None:
    """
    must serialize and parse back
    """
    for patch in (
            PkgbuildPatch("key", "value"),
            PkgbuildPatch("key", "4'2"),
            PkgbuildPatch("arch", ["i686", "x86_64"]),
            PkgbuildPatch("key", ["val'ue", "val\"ue2"]),
    ):
        assert PkgbuildPatch.from_env(patch.serialize()) == patch


def test_serialize_plain_diff() -> None:
    """
    must correctly serialize plain diff values
    """
    assert PkgbuildPatch(None, "{ value }").serialize() == "{ value }"


def test_serialize_function() -> None:
    """
    must correctly serialize function values
    """
    assert PkgbuildPatch("key()", "{ value }").serialize() == "key() { value }"


def test_serialize_list() -> None:
    """
    must correctly serialize list values
    """
    assert PkgbuildPatch("arch", ["i686", "x86_64"]).serialize() == """arch=(i686 x86_64)"""
    assert PkgbuildPatch("key", ["val'ue", "val\"ue2"]).serialize() == """key=('val'"'"'ue' 'val"ue2')"""


def test_substitute() -> None:
    """
    must correctly substitute variables
    """
    assert PkgbuildPatch("key", "$env $value").substitute({"env": "variable"}) == "variable $value"
    assert PkgbuildPatch("key", ["$env $value"]).substitute({"env": "variable"}) == ["variable $value"]


def test_write(mocker: MockerFixture) -> None:
    """
    must write serialized value to the file
    """
    file_mock = MagicMock()
    open_mock = mocker.patch("pathlib.Path.open")
    open_mock.return_value.__enter__.return_value = file_mock

    PkgbuildPatch("key", "value").write(Path("PKGBUILD"))
    open_mock.assert_called_once_with("a", encoding="utf8")
    file_mock.write.assert_has_calls([call("\n"), call("""key=value"""), call("\n")])
