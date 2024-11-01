#
# Copyright (c) 2021-2024 ahriman team.
#
# This file is part of ahriman
# (see https://github.com/arcan1s/ahriman).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import argparse
import getpass

from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.exceptions import PasswordError
from ahriman.core.formatters import UserPrinter
from ahriman.core.utils import enum_values
from ahriman.models.action import Action
from ahriman.models.repository_id import RepositoryId
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


class Users(Handler):
    """
    user management handler
    """

    ALLOW_MULTI_ARCHITECTURE_RUN = False  # system-wide action

    @classmethod
    def run(cls, args: argparse.Namespace, repository_id: RepositoryId, configuration: Configuration, *,
            report: bool) -> None:
        """
        callback for command line

        Args:
            args(argparse.Namespace): command line args
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting
        """
        database = SQLite.load(configuration)

        match args.action:
            case Action.Update:
                user = Users.user_create(args)
                # if password is left blank we are not going to require salt to be set
                salt = configuration.get("auth", "salt", fallback="") if user.password else ""
                database.user_update(user.hash_password(salt))
            case Action.List:
                users = database.user_list(args.username, args.role)
                for user in users:
                    UserPrinter(user)(verbose=True)
                Users.check_status(args.exit_code, users)
            case Action.Remove:
                database.user_remove(args.username)

    @staticmethod
    def _set_user_add_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for create user subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("user-add", help="create or update user",
                                 description="update user for web services with the given password and role. "
                                             "In case if password was not entered it will be asked interactively")
        parser.add_argument("username", help="username for web service")
        parser.add_argument("--key", help="optional PGP key used by this user. The private key must be imported")
        parser.add_argument("--packager", help="optional packager id used for build process in form of "
                                               "`Name Surname <mail@example.com>`")
        parser.add_argument(
            "-p", "--password", help="user password. Blank password will be treated as empty password, "
            "which is in particular must be used for OAuth2 authorization type.")
        parser.add_argument("-R", "--role", help="user access level",
                            type=UserAccess, choices=enum_values(UserAccess), default=UserAccess.Read)
        parser.set_defaults(action=Action.Update, architecture="", exit_code=False, lock=None, quiet=True,
                            report=False, repository="")
        return parser

    @staticmethod
    def _set_user_list_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for user list subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("user-list", help="user known users and their access",
                                 description="list users from the user mapping and their roles")
        parser.add_argument("username", help="filter users by username", nargs="?")
        parser.add_argument("-e", "--exit-code", help="return non-zero exit status if result is empty",
                            action="store_true")
        parser.add_argument("-R", "--role", help="filter users by role", type=UserAccess,
                            choices=enum_values(UserAccess))
        parser.set_defaults(action=Action.List, architecture="", lock=None, quiet=True, report=False, repository="",
                            unsafe=True)
        return parser

    @staticmethod
    def _set_user_remove_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for user removal subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("user-remove", help="remove user",
                                 description="remove user from the user mapping and update the configuration")
        parser.add_argument("username", help="username for web service")
        parser.set_defaults(action=Action.Remove, architecture="", exit_code=False, lock=None, quiet=True,
                            report=False, repository="")
        return parser

    @staticmethod
    def user_create(args: argparse.Namespace) -> User:
        """
        create user descriptor from arguments

        Args:
            args(argparse.Namespace): command line args

        Returns:
            User: built user descriptor

        Raises:
            PasswordError: password input is invalid
        """
        def read_password() -> str:
            first_password = getpass.getpass()
            second_password = getpass.getpass("Repeat password: ")
            if first_password != second_password:
                raise PasswordError("passwords don't match")
            return first_password

        password = args.password
        if password is None:
            password = read_password()

        return User(username=args.username, password=password, access=args.role,
                    packager_id=args.packager, key=args.key)

    arguments = [
        _set_user_add_parser,
        _set_user_list_parser,
        _set_user_remove_parser,
    ]
