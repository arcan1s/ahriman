import argparse
import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest import mock

from ahriman.application.handlers import CreateUser
from ahriman.core.configuration import Configuration
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases
    :param args: command line arguments fixture
    :return: generated arguments for these test cases
    """
    args.username = "user"
    args.password = "pa55w0rd"
    args.role = UserAccess.Status
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    create_configuration_mock = mocker.patch("ahriman.application.handlers.CreateUser.create_configuration")
    create_user = mocker.patch("ahriman.application.handlers.CreateUser.create_user")
    get_salt_mock = mocker.patch("ahriman.application.handlers.CreateUser.get_salt")

    CreateUser.run(args, "x86_64", configuration)
    create_configuration_mock.assert_called_once()
    create_user.assert_called_once()
    get_salt_mock.assert_called_once()


def test_create_configuration(user: User, mocker: MockerFixture) -> None:
    """
    must correctly create configuration file
    """
    section = Configuration.section_name("auth", user.access.value)

    mocker.patch("pathlib.Path.open")
    add_section_mock = mocker.patch("configparser.RawConfigParser.add_section")
    set_mock = mocker.patch("configparser.RawConfigParser.set")
    write_mock = mocker.patch("configparser.RawConfigParser.write")

    CreateUser.create_configuration(user, "salt", Path("path"))
    write_mock.assert_called_once()
    add_section_mock.assert_has_calls([mock.call("auth"), mock.call(section)])
    set_mock.assert_has_calls([
        mock.call("auth", "salt", pytest.helpers.anyvar(str)),
        mock.call(section, user.username, user.password)
    ])


def test_create_configuration_user_exists(configuration: Configuration, user: User, mocker: MockerFixture) -> None:
    """
    must correctly update configuration file if user already exists
    """
    section = Configuration.section_name("auth", user.access.value)
    configuration.add_section(section)
    configuration.set(section, user.username, "")

    mocker.patch("pathlib.Path.open")
    mocker.patch("configparser.ConfigParser", return_value=configuration)
    mocker.patch("configparser.RawConfigParser.write")
    add_section_mock = mocker.patch("configparser.RawConfigParser.add_section")

    CreateUser.create_configuration(user, "salt", Path("path"))
    add_section_mock.assert_not_called()
    assert configuration.get(section, user.username) == user.password


def test_create_configuration_file_exists(user: User, mocker: MockerFixture) -> None:
    """
    must correctly update configuration file if file already exists
    """
    mocker.patch("pathlib.Path.open")
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("configparser.RawConfigParser.write")
    read_mock = mocker.patch("configparser.RawConfigParser.read")

    CreateUser.create_configuration(user, "salt", Path("path"))
    read_mock.assert_called_once()


def test_create_user(args: argparse.Namespace, user: User) -> None:
    """
    must create user
    """
    args = _default_args(args)
    generated = CreateUser.create_user(args, "salt")
    assert generated.username == user.username
    assert generated.check_credentials(user.password, "salt")
    assert generated.access == user.access


def test_create_user_getpass(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must create user and get password from command line
    """
    args = _default_args(args)
    args.password = None

    getpass_mock = mocker.patch("getpass.getpass", return_value="password")
    generated = CreateUser.create_user(args, "salt")

    getpass_mock.assert_called_once()
    assert generated.check_credentials("password", "salt")


def test_get_salt_read(configuration: Configuration) -> None:
    """
    must read salt from configuration
    """
    assert CreateUser.get_salt(configuration) == "salt"


def test_get_salt_generate(configuration: Configuration) -> None:
    """
    must generate salt if it does not exist
    """
    configuration.remove_option("auth", "salt")

    salt = CreateUser.get_salt(configuration, 16)
    assert salt
    assert len(salt) == 16
