import os

from ahriman.core.configuration import Configuration
from ahriman.core.configuration.shell_interpolator import ShellInterpolator


def _parser() -> dict[str, dict[str, str]]:
    """
    parser mock

    Returns:
        dict[str, dict[str, str]]: options to be used as configparser mock
    """
    return {
        "section1": {
            "home": "$HOME",
            "key1": "value1",
            "key4": "${home}",
        },
        "section2": {
            "key2": "value2",
        },
        "section3": {
            "key3": "${section1:home}",
            "key5": "${section1:key4}",
        },
        "section4:suffix": {
            "key6": "value6"
        },
    }


def test_extract_variables() -> None:
    """
    must extract variables list
    """
    parser = _parser()

    assert dict(ShellInterpolator._extract_variables(parser, "${key1}", parser["section1"])) == {
        "key1": "value1",
    }
    assert not dict(ShellInterpolator._extract_variables(parser, "${key2}", parser["section1"]))

    assert dict(ShellInterpolator._extract_variables(parser, "${section2:key2}", parser["section1"])) == {
        "section2:key2": "value2",
    }
    assert not dict(ShellInterpolator._extract_variables(parser, "${section2:key1}", parser["section1"]))

    assert not dict(ShellInterpolator._extract_variables(parser, "${section4:key1}", parser["section1"]))

    assert dict(ShellInterpolator._extract_variables(parser, "${section4:suffix:key6}", parser["section1"])) == {
        "section4:suffix:key6": "value6",
    }


def test_environment() -> None:
    """
    must extend environment variables
    """
    assert "HOME" in ShellInterpolator.environment()
    assert "prefix" in ShellInterpolator.environment()


def test_before_get() -> None:
    """
    must correctly extract environment variables
    """
    interpolator = ShellInterpolator()
    assert interpolator.before_get({}, "", "", "value", {}) == "value"
    assert interpolator.before_get({}, "", "", "$value", {}) == "$value"
    assert interpolator.before_get({}, "", "", "$HOME", {}) == os.environ["HOME"]


def test_before_get_escaped() -> None:
    """
    must correctly read escaped variables
    """
    interpolator = ShellInterpolator()
    assert interpolator.before_get({}, "", "", "$$HOME", {}) == "$HOME"


def test_before_get_reference() -> None:
    """
    must correctly extract environment variables after resolving cross-reference
    """
    interpolator = ShellInterpolator()
    assert interpolator.before_get(_parser(), "", "", "${section1:home}", {}) == os.environ["HOME"]


def test_before_get_reference_recursive(configuration: Configuration) -> None:
    """
    must correctly extract environment variables after resolving cross-reference recursively
    """
    interpolator = ShellInterpolator()
    for section, items in _parser().items():
        for option, value in items.items():
            configuration.set_option(section, option, value)

    assert interpolator.before_get(configuration, "", "", "${section1:home}", {}) == os.environ["HOME"]
    assert interpolator.before_get(configuration, "", "", "${section3:key5}", {}) == os.environ["HOME"]
