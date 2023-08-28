#
# Copyright (c) 2021-2023 ahriman team.
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

from ahriman.application.handlers import Handler
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.exceptions import PasswordError
from ahriman.core.formatters import UserPrinter
from ahriman.models.action import Action
from ahriman.models.repository_id import RepositoryId
from ahriman.models.user import User


class Users(Handler):
    """
    user management handler
    """

    ALLOW_AUTO_ARCHITECTURE_RUN = False  # it should be called only as "no-architecture"

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
                Users.check_if_empty(args.exit_code, not users)
                for user in users:
                    UserPrinter(user).print(verbose=True)
            case Action.Remove:
                database.user_remove(args.username)

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
