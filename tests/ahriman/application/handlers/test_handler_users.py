import argparse
import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.application.handlers import Users
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.exceptions import InitializeError, PasswordError
from ahriman.models.action import Action
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.username = "user"
    args.action = Action.Update
    args.exit_code = False
    args.password = "pa55w0rd"
    args.role = UserAccess.Reporter
    args.secure = False
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, database: SQLite, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    user = User(username=args.username, password=args.password, access=args.role)
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    mocker.patch("ahriman.models.user.User.hash_password", return_value=user)
    get_auth_configuration_mock = mocker.patch("ahriman.application.handlers.Users.configuration_get")
    create_configuration_mock = mocker.patch("ahriman.application.handlers.Users.configuration_create")
    create_user_mock = mocker.patch("ahriman.application.handlers.Users.user_create", return_value=user)
    get_salt_mock = mocker.patch("ahriman.application.handlers.Users.get_salt", return_value=("salt", "salt"))
    update_mock = mocker.patch("ahriman.core.database.SQLite.user_update")

    Users.run(args, "x86_64", configuration, report=False, unsafe=False)
    get_auth_configuration_mock.assert_not_called()
    create_configuration_mock.assert_not_called()
    create_user_mock.assert_called_once_with(args)
    get_salt_mock.assert_called_once_with(configuration)
    update_mock.assert_called_once_with(user)


def test_run_empty_salt(args: argparse.Namespace, configuration: Configuration, database: SQLite,
                        mocker: MockerFixture) -> None:
    """
    must create configuration if salt was not set
    """
    args = _default_args(args)
    user = User(username=args.username, password=args.password, access=args.role)
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    mocker.patch("ahriman.models.user.User.hash_password", return_value=user)
    get_auth_configuration_mock = mocker.patch("ahriman.application.handlers.Users.configuration_get")
    create_configuration_mock = mocker.patch("ahriman.application.handlers.Users.configuration_create")
    create_user_mock = mocker.patch("ahriman.application.handlers.Users.user_create", return_value=user)
    get_salt_mock = mocker.patch("ahriman.application.handlers.Users.get_salt", return_value=(None, "salt"))
    update_mock = mocker.patch("ahriman.core.database.SQLite.user_update")

    Users.run(args, "x86_64", configuration, report=False, unsafe=False)
    get_auth_configuration_mock.assert_called_once_with(configuration.include)
    create_configuration_mock.assert_called_once_with(
        pytest.helpers.anyvar(int), pytest.helpers.anyvar(int), args.secure)
    create_user_mock.assert_called_once_with(args)
    get_salt_mock.assert_called_once_with(configuration)
    update_mock.assert_called_once_with(user)


def test_run_list(args: argparse.Namespace, configuration: Configuration, database: SQLite, user: User,
                  mocker: MockerFixture) -> None:
    """
    must list available users
    """
    args = _default_args(args)
    args.action = Action.List
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    check_mock = mocker.patch("ahriman.application.handlers.Handler.check_if_empty")
    list_mock = mocker.patch("ahriman.core.database.SQLite.user_list", return_value=[user])

    Users.run(args, "x86_64", configuration, report=False, unsafe=False)
    list_mock.assert_called_once_with("user", args.role)
    check_mock.assert_called_once_with(False, False)


def test_run_empty_exception(args: argparse.Namespace, configuration: Configuration, database: SQLite,
                             mocker: MockerFixture) -> None:
    """
    must raise ExitCode exception on empty user list
    """
    args = _default_args(args)
    args.action = Action.List
    args.exit_code = True
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    mocker.patch("ahriman.core.database.SQLite.user_list", return_value=[])
    check_mock = mocker.patch("ahriman.application.handlers.Handler.check_if_empty")

    Users.run(args, "x86_64", configuration, report=False, unsafe=False)
    check_mock.assert_called_once_with(True, True)


def test_run_remove(args: argparse.Namespace, configuration: Configuration, database: SQLite,
                    mocker: MockerFixture) -> None:
    """
    must remove user if remove flag supplied
    """
    args = _default_args(args)
    args.action = Action.Remove
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    remove_mock = mocker.patch("ahriman.core.database.SQLite.user_remove")

    Users.run(args, "x86_64", configuration, report=False, unsafe=False)
    remove_mock.assert_called_once_with(args.username)


def test_configuration_create(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must correctly create configuration file
    """
    mocker.patch("pathlib.Path.open")
    set_mock = mocker.patch("ahriman.core.configuration.Configuration.set_option")
    write_mock = mocker.patch("ahriman.application.handlers.Users.configuration_write")

    Users.configuration_create(configuration, "salt", False)
    set_mock.assert_called_once_with("auth", "salt", pytest.helpers.anyvar(int))
    write_mock.assert_called_once_with(configuration, False)


def test_configuration_get(mocker: MockerFixture) -> None:
    """
    must load configuration from filesystem
    """
    mocker.patch("pathlib.Path.open")
    mocker.patch("pathlib.Path.is_file", return_value=True)
    read_mock = mocker.patch("ahriman.core.configuration.Configuration.read")

    assert Users.configuration_get(Path("path"))
    read_mock.assert_called_once_with(Path("path") / "00-auth.ini")


def test_configuration_write(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must write configuration
    """
    mocker.patch("pathlib.Path.open")
    write_mock = mocker.patch("ahriman.core.configuration.Configuration.write")
    chmod_mock = mocker.patch("pathlib.Path.chmod")

    Users.configuration_write(configuration, secure=True)
    write_mock.assert_called_once_with(pytest.helpers.anyvar(int))
    chmod_mock.assert_called_once_with(0o600)


def test_configuration_write_insecure(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must write configuration without setting file permissions
    """
    mocker.patch("pathlib.Path.open")
    mocker.patch("ahriman.core.configuration.Configuration.write")
    chmod_mock = mocker.patch("pathlib.Path.chmod")

    Users.configuration_write(configuration, secure=False)
    chmod_mock.assert_not_called()


def test_configuration_write_not_loaded(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must do nothing in case if configuration is not loaded
    """
    configuration.path = None
    mocker.patch("pathlib.Path.open")

    with pytest.raises(InitializeError):
        Users.configuration_write(configuration, secure=True)


def test_get_salt_read(configuration: Configuration) -> None:
    """
    must read salt from configuration
    """
    assert Users.get_salt(configuration) == ("salt", "salt")


def test_get_salt_generate(configuration: Configuration) -> None:
    """
    must generate salt if it does not exist
    """
    configuration.remove_option("auth", "salt")

    old_salt, salt = Users.get_salt(configuration, 16)
    assert salt
    assert old_salt is None
    assert len(salt) == 16


def test_user_create(args: argparse.Namespace, user: User) -> None:
    """
    must create user
    """
    args = _default_args(args)
    generated = Users.user_create(args)
    assert generated.username == user.username
    assert generated.access == user.access


def test_user_create_getpass(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must create user and get password from command line
    """
    args = _default_args(args)
    args.password = None
    getpass_mock = mocker.patch("getpass.getpass", return_value="password")

    generated = Users.user_create(args)
    getpass_mock.assert_has_calls([MockCall(), MockCall("Repeat password: ")])
    assert generated.password == "password"


def test_user_create_getpass_exception(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must raise password error in case if password doesn't match
    """
    args = _default_args(args)
    args.password = None
    mocker.patch("getpass.getpass", side_effect=lambda *_: User.generate_password(10))

    with pytest.raises(PasswordError):
        Users.user_create(args)


def test_disallow_auto_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Users.ALLOW_AUTO_ARCHITECTURE_RUN
