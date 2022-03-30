#
# Copyright (c) 2021 ahriman team.
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
from typing import Type

from ahriman.application.handlers.handler import Handler
from ahriman.core.configuration import Configuration
from ahriman.core.database.sqlite import SQLite
from ahriman.core.formatters.user_printer import UserPrinter
from ahriman.models.action import Action
from ahriman.models.user import User as MUser


class User(Handler):
    """
    user management handler
    """

    ALLOW_AUTO_ARCHITECTURE_RUN = False  # it should be called only as "no-architecture"

    @classmethod
    def run(cls: Type[Handler], args: argparse.Namespace, architecture: str,
            configuration: Configuration, no_report: bool, unsafe: bool) -> None:
        """
        callback for command line
        :param args: command line args
        :param architecture: repository architecture
        :param configuration: configuration instance
        :param no_report: force disable reporting
        :param unsafe: if set no user check will be performed before path creation
        """
        salt = User.get_salt(configuration)
        user = User.user_create(args)

        auth_configuration = User.configuration_get(configuration.include)
        database = SQLite.load(configuration)

        if args.action == Action.List:
            for found_user in database.user_list(user.username, user.access):
                UserPrinter(found_user).print(verbose=True)
        elif args.action == Action.Remove:
            database.user_remove(user.username)
        elif args.action == Action.Update:
            User.configuration_create(auth_configuration, user, salt, args.as_service, args.secure)
            database.user_update(user.hash_password(salt))

    @staticmethod
    def configuration_create(configuration: Configuration, user: MUser, salt: str,
                             as_service_user: bool, secure: bool) -> None:
        """
        enable configuration if it has been disabled
        :param configuration: configuration instance
        :param user: user descriptor
        :param salt: password hash salt
        :param as_service_user: add user as service user, also set password and user to configuration
        :param secure: if true then set file permissions to 0o600
        """
        configuration.set_option("auth", "salt", salt)
        if as_service_user:
            configuration.set_option("web", "username", user.username)
            configuration.set_option("web", "password", user.password)
        User.configuration_write(configuration, secure)

    @staticmethod
    def configuration_get(include_path: Path) -> Configuration:
        """
        create configuration instance
        :param include_path: path to directory with configuration includes
        :return: configuration instance. In case if there are local settings they will be loaded
        """
        target = include_path / "auth.ini"
        configuration = Configuration()
        configuration.load(target)

        configuration.architecture = ""  # not user anyway

        return configuration

    @staticmethod
    def configuration_write(configuration: Configuration, secure: bool) -> None:
        """
        write configuration file
        :param configuration: configuration instance
        :param secure: if true then set file permissions to 0o600
        """
        path, _ = configuration.check_loaded()
        with path.open("w") as ahriman_configuration:
            configuration.write(ahriman_configuration)
        if secure:
            path.chmod(0o600)

    @staticmethod
    def get_salt(configuration: Configuration, salt_length: int = 20) -> str:
        """
        get salt from configuration or create new string
        :param configuration: configuration instance
        :param salt_length: salt length
        :return: current salt
        """
        if salt := configuration.get("auth", "salt", fallback=None):
            return salt
        return MUser.generate_password(salt_length)

    @staticmethod
    def user_create(args: argparse.Namespace) -> MUser:
        """
        create user descriptor from arguments
        :param args: command line args
        :return: built user descriptor
        """
        user = MUser(args.username, args.password, args.role)
        if user.password is None:
            user.password = getpass.getpass()
        return user
