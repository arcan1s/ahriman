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

from pathlib import Path

from ahriman.application.handlers import Handler
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.exceptions import PasswordError
from ahriman.core.formatters import UserPrinter
from ahriman.models.action import Action
from ahriman.models.user import User


class Users(Handler):
    """
    user management handler
    """

    ALLOW_AUTO_ARCHITECTURE_RUN = False  # it should be called only as "no-architecture"

    @classmethod
    def run(cls, args: argparse.Namespace, architecture: str, configuration: Configuration, *,
            report: bool, unsafe: bool) -> None:
        """
        callback for command line

        Args:
            args(argparse.Namespace): command line args
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting
            unsafe(bool): if set no user check will be performed before path creation
        """
        database = SQLite.load(configuration)

        if args.action == Action.Update:
            old_salt, salt = Users.get_salt(configuration)
            user = Users.user_create(args)

            if old_salt is None:
                auth_configuration = Users.configuration_get(configuration.include)
                Users.configuration_create(auth_configuration, salt, args.secure)

            database.user_update(user.hash_password(salt))
        elif args.action == Action.List:
            users = database.user_list(args.username, args.role)
            Users.check_if_empty(args.exit_code, not users)
            for user in users:
                UserPrinter(user).print(verbose=True)
        elif args.action == Action.Remove:
            database.user_remove(args.username)

    @staticmethod
    def configuration_create(configuration: Configuration, salt: str, secure: bool) -> None:
        """
        enable configuration if it has been disabled

        Args:
            configuration(Configuration): configuration instance
            salt(str): password hash salt
            secure(bool): if true then set file permissions to 0o600
        """
        configuration.set_option("auth", "salt", salt)
        Users.configuration_write(configuration, secure)

    @staticmethod
    def configuration_get(include_path: Path) -> Configuration:
        """
        create configuration instance

        Args:
            include_path(Path): path to directory with configuration includes

        Returns:
            Configuration: configuration instance. In case if there are local settings they will be loaded
        """
        target = include_path / "00-auth.ini"
        configuration = Configuration()
        configuration.load(target)

        configuration.architecture = ""  # not user anyway

        return configuration

    @staticmethod
    def configuration_write(configuration: Configuration, secure: bool) -> None:
        """
        write configuration file

        Args:
            configuration(Configuration): configuration instance
            secure(bool): if true then set file permissions to 0o600
        """
        path, _ = configuration.check_loaded()
        with path.open("w") as ahriman_configuration:
            configuration.write(ahriman_configuration)
        if secure:
            path.chmod(0o600)

    @staticmethod
    def get_salt(configuration: Configuration, salt_length: int = 20) -> tuple[str | None, str]:
        """
        get salt from configuration or create new string

        Args:
            configuration(Configuration): configuration instance
            salt_length(int, optional): salt length (Default value = 20)

        Returns:
            tuple[str | None, str]: tuple containing salt from configuration if any and actual salt which must be
                used for password hash
        """
        if salt := configuration.get("auth", "salt", fallback=None):
            return salt, salt
        return None, User.generate_password(salt_length)

    @staticmethod
    def user_create(args: argparse.Namespace) -> User:
        """
        create user descriptor from arguments

        Args:
            args(argparse.Namespace): command line args

        Returns:
            User: built user descriptor
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

        return User(username=args.username, password=password, access=args.role)
