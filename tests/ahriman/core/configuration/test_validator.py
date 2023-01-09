from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.core.configuration.validator import Validator


def test_types_mapping() -> None:
    """
    must set custom types
    """
    assert "path" in Validator.types_mapping
    assert Path in Validator.types_mapping["path"].included_types


def test_normalize_coerce_absolute_path(validator: Validator) -> None:
    """
    must convert string value to path by using configuration converters
    """
    convert_mock = MagicMock()
    validator.instance.converters["path"] = convert_mock

    validator._normalize_coerce_absolute_path("value")
    convert_mock.assert_called_once_with("value")


def test_normalize_coerce_boolean(validator: Validator, mocker: MockerFixture) -> None:
    """
    must convert string value to boolean by using configuration converters
    """
    convert_mock = mocker.patch("ahriman.core.configuration.Configuration._convert_to_boolean")
    validator._normalize_coerce_boolean("1")
    convert_mock.assert_called_once_with("1")


def test_normalize_coerce_integer(validator: Validator) -> None:
    """
    must convert string value to integer by using configuration converters
    """
    assert validator._normalize_coerce_integer("1") == 1
    assert validator._normalize_coerce_integer("42") == 42


def test_normalize_coerce_list(validator: Validator) -> None:
    """
    must convert string value to list by using configuration converters
    """
    convert_mock = MagicMock()
    validator.instance.converters["list"] = convert_mock

    validator._normalize_coerce_list("value")
    convert_mock.assert_called_once_with("value")


def test_validate_path_exists(validator: Validator, mocker: MockerFixture) -> None:
    """
    must validate that paths exists
    """
    error_mock = mocker.patch("ahriman.core.configuration.validator.Validator._error")

    mocker.patch("pathlib.Path.exists", return_value=False)
    validator._validate_path_exists(False, "field", Path("1"))

    mocker.patch("pathlib.Path.exists", return_value=False)
    validator._validate_path_exists(True, "field", Path("2"))

    mocker.patch("pathlib.Path.exists", return_value=True)
    validator._validate_path_exists(True, "field", Path("3"))

    error_mock.assert_called_once_with("field", "Path 2 must exist")
