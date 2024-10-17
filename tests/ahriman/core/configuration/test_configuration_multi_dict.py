import pytest

from ahriman.core.configuration.configuration_multi_dict import ConfigurationMultiDict
from ahriman.core.exceptions import OptionError


def test_setitem_non_list() -> None:
    """
    must insert not list correctly
    """
    instance = ConfigurationMultiDict()
    instance["key"] = "value"
    assert instance["key"] == "value"


def test_setitem_remove() -> None:
    """
    must remove key
    """
    instance = ConfigurationMultiDict()
    instance["key"] = "value"
    instance["key"] = [""]

    assert "key" not in instance


def test_setitem_array() -> None:
    """
    must set array correctly
    """
    instance = ConfigurationMultiDict()
    instance["key[]"] = ["value1"]
    instance["key[]"] = ["value2"]

    assert instance["key"] == ["value1 value2"]


def test_setitem_array_exception() -> None:
    """
    must raise exception if the current value is not a single value array
    """
    instance = ConfigurationMultiDict()
    instance["key[]"] = ["value1", "value2"]
    with pytest.raises(OptionError):
        instance["key[]"] = ["value3"]


def test_setitem_exception() -> None:
    """
    must raise exception on invalid key
    """
    instance = ConfigurationMultiDict()
    with pytest.raises(OptionError):
        instance["prefix[]suffix"] = "value"
