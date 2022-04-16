import argparse
import pytest

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.application.handlers import User
from ahriman.core.configuration import Configuration
from ahriman.core.database.sqlite import SQLite
from ahriman.core.exceptions import InitializeException
from ahriman.models.action import Action
from ahriman.models.user import User as MUser
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
    args.as_service = False
    args.exit_code = False
    args.password = "pa55w0rd"
    args.role = UserAccess.Read
    args.secure = False
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, database: SQLite, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    user = MUser(args.username, args.password, args.role)
    mocker.patch("ahriman.core.database.sqlite.SQLite.load", return_value=database)
    mocker.patch("ahriman.models.user.User.hash_password", return_value=user)
    get_auth_configuration_mock = mocker.patch("ahriman.application.handlers.User.configuration_get")
    create_configuration_mock = mocker.patch("ahriman.application.handlers.User.configuration_create")
    create_user_mock = mocker.patch("ahriman.application.handlers.User.user_create", return_value=user)
    get_salt_mock = mocker.patch("ahriman.application.handlers.User.get_salt", return_value="salt")
    update_mock = mocker.patch("ahriman.core.database.sqlite.SQLite.user_update")

    User.run(args, "x86_64", configuration, True, False)
    get_auth_configuration_mock.assert_called_once_with(configuration.include)
    create_configuration_mock.assert_called_once_with(pytest.helpers.anyvar(int), pytest.helpers.anyvar(int),
                                                      pytest.helpers.anyvar(int), args.as_service, args.secure)
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
    mocker.patch("ahriman.core.database.sqlite.SQLite.load", return_value=database)
    check_mock = mocker.patch("ahriman.application.handlers.handler.Handler.check_if_empty")
    list_mock = mocker.patch("ahriman.core.database.sqlite.SQLite.user_list", return_value=[user])

    User.run(args, "x86_64", configuration, True, False)
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
    mocker.patch("ahriman.core.database.sqlite.SQLite.load", return_value=database)
    mocker.patch("ahriman.core.database.sqlite.SQLite.user_list", return_value=[])
    check_mock = mocker.patch("ahriman.application.handlers.handler.Handler.check_if_empty")

    User.run(args, "x86_64", configuration, True, False)
    check_mock.assert_called_once_with(True, True)


def test_run_remove(args: argparse.Namespace, configuration: Configuration, database: SQLite,
                    mocker: MockerFixture) -> None:
    """
    must remove user if remove flag supplied
    """
    args = _default_args(args)
    args.action = Action.Remove
    mocker.patch("ahriman.core.database.sqlite.SQLite.load", return_value=database)
    remove_mock = mocker.patch("ahriman.core.database.sqlite.SQLite.user_remove")

    User.run(args, "x86_64", configuration, True, False)
    remove_mock.assert_called_once_with(args.username)


def test_configuration_create(configuration: Configuration, user: MUser, mocker: MockerFixture) -> None:
    """
    must correctly create configuration file
    """
    mocker.patch("pathlib.Path.open")
    set_mock = mocker.patch("ahriman.core.configuration.Configuration.set_option")
    write_mock = mocker.patch("ahriman.application.handlers.User.configuration_write")

    User.configuration_create(configuration, user, "salt", False, False)
    set_mock.assert_called_once_with("auth", "salt", pytest.helpers.anyvar(int))
    write_mock.assert_called_once_with(configuration, False)


def test_configuration_create_with_plain_password(
        configuration: Configuration,
        user: MUser,
        mocker: MockerFixture) -> None:
    """
    must set plain text password and user for the service
    """
    mocker.patch("pathlib.Path.open")

    User.configuration_create(configuration, user, "salt", True, False)

    generated = MUser.from_option(user.username, user.password).hash_password("salt")
    service = MUser.from_option(configuration.get("web", "username"), configuration.get("web", "password"))
    assert generated.username == service.username
    assert generated.check_credentials(service.password, configuration.get("auth", "salt"))


def test_configuration_get(mocker: MockerFixture) -> None:
    """
    must load configuration from filesystem
    """
    mocker.patch("pathlib.Path.open")
    mocker.patch("pathlib.Path.is_file", return_value=True)
    read_mock = mocker.patch("ahriman.core.configuration.Configuration.read")

    assert User.configuration_get(Path("path"))
    read_mock.assert_called_once_with(Path("path") / "auth.ini")


def test_configuration_write(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must write configuration
    """
    mocker.patch("pathlib.Path.open")
    write_mock = mocker.patch("ahriman.core.configuration.Configuration.write")
    chmod_mock = mocker.patch("pathlib.Path.chmod")

    User.configuration_write(configuration, secure=True)
    write_mock.assert_called_once_with(pytest.helpers.anyvar(int))
    chmod_mock.assert_called_once_with(0o600)


def test_configuration_write_insecure(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must write configuration without setting file permissions
    """
    mocker.patch("pathlib.Path.open")
    mocker.patch("ahriman.core.configuration.Configuration.write")
    chmod_mock = mocker.patch("pathlib.Path.chmod")

    User.configuration_write(configuration, secure=False)
    chmod_mock.assert_not_called()


def test_configuration_write_not_loaded(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must do nothing in case if configuration is not loaded
    """
    configuration.path = None
    mocker.patch("pathlib.Path.open")

    with pytest.raises(InitializeException):
        User.configuration_write(configuration, secure=True)


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


def test_user_create(args: argparse.Namespace, user: MUser) -> None:
    """
    must create user
    """
    args = _default_args(args)
    generated = User.user_create(args)
    assert generated.username == user.username
    assert generated.access == user.access


def test_user_create_getpass(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must create user and get password from command line
    """
    args = _default_args(args)
    args.password = None

    getpass_mock = mocker.patch("getpass.getpass", return_value="password")
    generated = User.user_create(args)

    getpass_mock.assert_called_once_with()
    assert generated.password == "password"


def test_disallow_auto_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not User.ALLOW_AUTO_ARCHITECTURE_RUN
