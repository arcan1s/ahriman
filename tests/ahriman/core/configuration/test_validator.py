from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import MagicMock, call as MockCall

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
    validator.configuration.converters["path"] = convert_mock

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
    validator.configuration.converters["list"] = convert_mock

    validator._normalize_coerce_list("value")
    convert_mock.assert_called_once_with("value")


def test_validate_is_ip_address(validator: Validator, mocker: MockerFixture) -> None:
    """
    must validate addresses correctly
    """
    error_mock = mocker.patch("ahriman.core.configuration.validator.Validator._error")

    validator._validate_is_ip_address(["localhost"], "field", "localhost")
    validator._validate_is_ip_address([], "field", "localhost")

    validator._validate_is_ip_address([], "field", "127.0.0.1")
    validator._validate_is_ip_address([], "field", "::")
    validator._validate_is_ip_address([], "field", "0.0.0.0")

    validator._validate_is_ip_address([], "field", "random string")

    error_mock.assert_has_calls([
        MockCall("field", "Value localhost must be valid IP address"),
        MockCall("field", "Value random string must be valid IP address"),
    ])


def test_validate_is_url(validator: Validator, mocker: MockerFixture) -> None:
    """
    must validate url correctly
    """
    error_mock = mocker.patch("ahriman.core.configuration.validator.Validator._error")

    validator._validate_is_url([], "field", "http://example.com")
    validator._validate_is_url([], "field", "https://example.com")
    validator._validate_is_url([], "field", "file:///tmp")

    validator._validate_is_url(["http", "https"], "field", "file:///tmp")

    validator._validate_is_url([], "field", "http:///path")

    validator._validate_is_url([], "field", "random string")

    error_mock.assert_has_calls([
        MockCall("field", "Url file:///tmp scheme must be one of ['http', 'https']"),
        MockCall("field", "Location must be set for url http:///path of scheme http"),
        MockCall("field", "Url scheme is not set for random string"),
    ])


def test_validate_path_exists(validator: Validator, mocker: MockerFixture) -> None:
    """
    must validate that paths exists
    """
    error_mock = mocker.patch("ahriman.core.configuration.validator.Validator._error")

    mocker.patch("pathlib.Path.exists", return_value=False)
    validator._validate_path_exists(False, "field", Path("1"))

    mocker.patch("pathlib.Path.exists", return_value=True)
    validator._validate_path_exists(False, "field", Path("2"))

    mocker.patch("pathlib.Path.exists", return_value=False)
    validator._validate_path_exists(True, "field", Path("3"))

    mocker.patch("pathlib.Path.exists", return_value=True)
    validator._validate_path_exists(True, "field", Path("4"))

    error_mock.assert_has_calls([
        MockCall("field", "Path 2 must not exist"),
        MockCall("field", "Path 3 must exist"),
    ])
