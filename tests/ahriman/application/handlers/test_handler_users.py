import argparse
import configparser

import pytest

from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.application.handlers import Users
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.exceptions import PasswordError
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
    args.key = "key"
    args.packager = "packager"
    args.password = "pa55w0rd"
    args.role = UserAccess.Reporter
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, database: SQLite, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    user = User(username=args.username, password=args.password, access=args.role,
                packager_id=args.packager, key=args.key)
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    mocker.patch("ahriman.models.user.User.hash_password", return_value=user)
    create_user_mock = mocker.patch("ahriman.application.handlers.Users.user_create", return_value=user)
    update_mock = mocker.patch("ahriman.core.database.SQLite.user_update")

    _, repository_id = configuration.check_loaded()
    Users.run(args, repository_id, configuration, report=False)
    create_user_mock.assert_called_once_with(args)
    update_mock.assert_called_once_with(user)


def test_run_empty_salt(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must process users with empty password salt
    """
    configuration.remove_option("auth", "salt")
    args = _default_args(args)
    user = User(username=args.username, password=args.password, access=args.role,
                packager_id=args.packager, key=args.key)
    mocker.patch("ahriman.models.user.User.hash_password", return_value=user)
    create_user_mock = mocker.patch("ahriman.application.handlers.Users.user_create", return_value=user)
    update_mock = mocker.patch("ahriman.core.database.SQLite.user_update")

    _, repository_id = configuration.check_loaded()
    Users.run(args, repository_id, configuration, report=False)
    create_user_mock.assert_called_once_with(args)
    update_mock.assert_called_once_with(user)


def test_run_empty_salt_without_password(args: argparse.Namespace, configuration: Configuration, database: SQLite,
                                         mocker: MockerFixture) -> None:
    """
    must skip salt option in case if password was empty
    """
    configuration.remove_option("auth", "salt")
    args = _default_args(args)
    user = User(username=args.username, password="", access=args.role,
                packager_id=args.packager, key=args.key)
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    mocker.patch("ahriman.models.user.User.hash_password", return_value=user)
    create_user_mock = mocker.patch("ahriman.application.handlers.Users.user_create", return_value=user)
    update_mock = mocker.patch("ahriman.core.database.SQLite.user_update")

    _, repository_id = configuration.check_loaded()
    Users.run(args, repository_id, configuration, report=False)
    create_user_mock.assert_called_once_with(args)
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

    _, repository_id = configuration.check_loaded()
    Users.run(args, repository_id, configuration, report=False)
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

    _, repository_id = configuration.check_loaded()
    Users.run(args, repository_id, configuration, report=False)
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

    _, repository_id = configuration.check_loaded()
    Users.run(args, repository_id, configuration, report=False)
    remove_mock.assert_called_once_with(args.username)


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
