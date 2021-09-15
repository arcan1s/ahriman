import argparse
import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest import mock

from ahriman.application.handlers import User
from ahriman.core.configuration import Configuration
from ahriman.models.user import User as MUser
from ahriman.models.user_access import UserAccess


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases
    :param args: command line arguments fixture
    :return: generated arguments for these test cases
    """
    args.username = "user"
    args.password = "pa55w0rd"
    args.access = UserAccess.Read
    args.as_service = False
    args.remove = False
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    get_auth_configuration_mock = mocker.patch("ahriman.application.handlers.User.get_auth_configuration")
    create_configuration_mock = mocker.patch("ahriman.application.handlers.User.create_configuration")
    write_configuration_mock = mocker.patch("ahriman.application.handlers.User.write_configuration")
    create_user = mocker.patch("ahriman.application.handlers.User.create_user")
    get_salt_mock = mocker.patch("ahriman.application.handlers.User.get_salt")

    User.run(args, "x86_64", configuration, True)
    get_auth_configuration_mock.assert_called_once()
    create_configuration_mock.assert_called_once()
    create_user.assert_called_once()
    get_salt_mock.assert_called_once()
    write_configuration_mock.assert_called_once()


def test_run_remove(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must remove user if remove flag supplied
    """
    args = _default_args(args)
    args.remove = True
    get_auth_configuration_mock = mocker.patch("ahriman.application.handlers.User.get_auth_configuration")
    create_configuration_mock = mocker.patch("ahriman.application.handlers.User.create_configuration")
    write_configuration_mock = mocker.patch("ahriman.application.handlers.User.write_configuration")

    User.run(args, "x86_64", configuration, True)
    get_auth_configuration_mock.assert_called_once()
    create_configuration_mock.assert_not_called()
    write_configuration_mock.assert_called_once()


def test_clear_user(configuration: Configuration, user: MUser) -> None:
    """
    must clear user from configuration
    """
    section = Configuration.section_name("auth", user.access.value)
    configuration.set_option(section, user.username, user.password)

    User.clear_user(configuration, user)
    assert configuration.get(section, user.username, fallback=None) is None


def test_clear_user_multiple_sections(configuration: Configuration, user: MUser) -> None:
    """
    must clear user from configuration from all sections
    """
    for role in UserAccess:
        section = Configuration.section_name("auth", role.value)
        configuration.set_option(section, user.username, user.password)

    User.clear_user(configuration, user)
    for role in UserAccess:
        section = Configuration.section_name("auth", role.value)
        assert configuration.get(section, user.username, fallback=None) is None


def test_create_configuration(configuration: Configuration, user: MUser, mocker: MockerFixture) -> None:
    """
    must correctly create configuration file
    """
    section = Configuration.section_name("auth", user.access.value)
    mocker.patch("pathlib.Path.open")
    set_mock = mocker.patch("ahriman.core.configuration.Configuration.set_option")

    User.create_configuration(configuration, user, "salt", False)
    set_mock.assert_has_calls([
        mock.call("auth", "salt", pytest.helpers.anyvar(str)),
        mock.call(section, user.username, pytest.helpers.anyvar(str))
    ])


def test_create_configuration_user_exists(configuration: Configuration, user: MUser, mocker: MockerFixture) -> None:
    """
    must correctly update configuration file if user already exists
    """
    section = Configuration.section_name("auth", user.access.value)
    configuration.set_option(section, user.username, "")
    mocker.patch("pathlib.Path.open")

    User.create_configuration(configuration, user, "salt", False)
    generated = MUser.from_option(user.username, configuration.get(section, user.username))
    assert generated.check_credentials(user.password, configuration.get("auth", "salt"))


def test_create_configuration_with_plain_password(
        configuration: Configuration,
        user: MUser,
        mocker: MockerFixture) -> None:
    """
    must set plain text password and user for the service
    """
    section = Configuration.section_name("auth", user.access.value)
    mocker.patch("pathlib.Path.open")

    User.create_configuration(configuration, user, "salt", True)

    generated = MUser.from_option(user.username, configuration.get(section, user.username))
    service = MUser.from_option(configuration.get("web", "username"), configuration.get("web", "password"))
    assert generated.username == service.username
    assert generated.check_credentials(service.password, configuration.get("auth", "salt"))


def test_create_user(args: argparse.Namespace, user: MUser) -> None:
    """
    must create user
    """
    args = _default_args(args)
    generated = User.create_user(args)
    assert generated.username == user.username
    assert generated.access == user.access


def test_create_user_getpass(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must create user and get password from command line
    """
    args = _default_args(args)
    args.password = None

    getpass_mock = mocker.patch("getpass.getpass", return_value="password")
    generated = User.create_user(args)

    getpass_mock.assert_called_once()
    assert generated.password == "password"


def test_get_salt_read(configuration: Configuration) -> None:
    """
    must read salt from configuration
    """
    assert User.get_salt(configuration) == "salt"


def test_get_salt_generate(configuration: Configuration) -> None:
    """
    must generate salt if it does not exist
    """
    configuration.remove_option("auth", "salt")

    salt = User.get_salt(configuration, 16)
    assert salt
    assert len(salt) == 16


def test_get_auth_configuration_exists(mocker: MockerFixture) -> None:
    """
    must load configuration from filesystem
    """
    mocker.patch("pathlib.Path.open")
    mocker.patch("pathlib.Path.is_file", return_value=True)
    read_mock = mocker.patch("ahriman.core.configuration.Configuration.read")

    assert User.get_auth_configuration(Path("path"))
    read_mock.assert_called_once()


def test_get_auth_configuration_not_exists(mocker: MockerFixture) -> None:
    """
    must try to load configuration from filesystem
    """
    mocker.patch("pathlib.Path.open")
    mocker.patch("pathlib.Path.is_file", return_value=False)
    read_mock = mocker.patch("ahriman.core.configuration.Configuration.read")

    assert User.get_auth_configuration(Path("path"))
    read_mock.assert_called_once()


def test_write_configuration(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must write configuration
    """
    mocker.patch("pathlib.Path.open")
    write_mock = mocker.patch("ahriman.core.configuration.Configuration.write")
    chmod_mock = mocker.patch("pathlib.Path.chmod")

    User.write_configuration(configuration)
    write_mock.assert_called_once()
    chmod_mock.assert_called_once()


def test_write_configuration_not_loaded(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must do nothing in case if configuration is not loaded
    """
    configuration.path = None
    mocker.patch("pathlib.Path.open")
    write_mock = mocker.patch("ahriman.core.configuration.Configuration.write")
    chmod_mock = mocker.patch("pathlib.Path.chmod")

    User.write_configuration(configuration)
    write_mock.assert_not_called()
    chmod_mock.assert_not_called()
