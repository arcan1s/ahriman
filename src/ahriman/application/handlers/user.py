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

from ahriman.application.application import Application
from ahriman.application.handlers.handler import Handler
from ahriman.core.configuration import Configuration
from ahriman.models.action import Action
from ahriman.models.user import User as MUser
from ahriman.models.user_access import UserAccess


class User(Handler):
    """
    user management handler
    """

    ALLOW_AUTO_ARCHITECTURE_RUN = False  # it should be called only as "no-architecture"

    @classmethod
    def run(cls: Type[Handler], args: argparse.Namespace, architecture: str,
            configuration: Configuration, no_report: bool) -> None:
        """
        callback for command line
        :param args: command line args
        :param architecture: repository architecture
        :param configuration: configuration instance
        :param no_report: force disable reporting
        """
        salt = User.get_salt(configuration)
        user = User.create_user(args)
        auth_configuration = User.get_auth_configuration(configuration.include)

        User.clear_user(auth_configuration, user)
        if args.action == Action.Update:
            User.create_configuration(auth_configuration, user, salt, args.as_service)
        User.write_configuration(auth_configuration, args.secure)

        if not args.no_reload:
            client = Application(architecture, configuration, no_report=False).repository.reporter
            client.reload_auth()

    @staticmethod
    def clear_user(configuration: Configuration, user: MUser) -> None:
        """
        remove user user from configuration file in case if it exists
        :param configuration: configuration instance
        :param user: user descriptor
        """
        for role in UserAccess:
            section = Configuration.section_name("auth", role.value)
            if not configuration.has_option(section, user.username):
                continue
            configuration.remove_option(section, user.username)

    @staticmethod
    def create_configuration(configuration: Configuration, user: MUser, salt: str, as_service_user: bool) -> None:
        """
        put new user to configuration
        :param configuration: configuration instance
        :param user: user descriptor
        :param salt: password hash salt
        :param as_service_user: add user as service user, also set password and user to configuration
        """
        section = Configuration.section_name("auth", user.access.value)
        configuration.set_option("auth", "salt", salt)
        configuration.set_option(section, user.username, user.hash_password(salt))

        if as_service_user:
            configuration.set_option("web", "username", user.username)
            configuration.set_option("web", "password", user.password)

    @staticmethod
    def create_user(args: argparse.Namespace) -> MUser:
        """
        create user descriptor from arguments
        :param args: command line args
        :return: built user descriptor
        """
        user = MUser(args.username, args.password, args.role)
        if user.password is None:
            user.password = getpass.getpass()
        return user

    @staticmethod
    def get_auth_configuration(include_path: Path) -> Configuration:
        """
        create configuration instance
        :param include_path: path to directory with configuration includes
        :return: configuration instance. In case if there are local settings they will be loaded
        """
        target = include_path / "auth.ini"
        configuration = Configuration()
        configuration.load(target)

        return configuration

    @staticmethod
    def get_salt(configuration: Configuration, salt_length: int = 20) -> str:
        """
        get salt from configuration or create new string
        :param configuration: configuration instance
        :param salt_length: salt length
        :return: current salt
        """
        salt = configuration.get("auth", "salt", fallback=None)
        if salt:
            return salt
        return MUser.generate_password(salt_length)

    @staticmethod
    def write_configuration(configuration: Configuration, secure: bool) -> None:
        """
        write configuration file
        :param configuration: configuration instance
        :param secure: if true then set file permissions to 0o600
        """
        if configuration.path is None:
            return  # should never happen actually
        with configuration.path.open("w") as ahriman_configuration:
            configuration.write(ahriman_configuration)
        if secure:
            configuration.path.chmod(0o600)
