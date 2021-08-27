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
import configparser

from getpass import getpass
from pathlib import Path
from typing import Type

from ahriman.application.handlers.handler import Handler
from ahriman.core.configuration import Configuration
from ahriman.models.user import User


class CreateUser(Handler):
    """
    create user handler
    """

    @classmethod
    def run(cls: Type[Handler], args: argparse.Namespace, architecture: str, configuration: Configuration) -> None:
        """
        callback for command line
        :param args: command line args
        :param architecture: repository architecture
        :param configuration: configuration instance
        """
        user = CreateUser.create_user(args, configuration)
        CreateUser.create_configuration(user, configuration.include)

    @staticmethod
    def create_configuration(user: User, include_path: Path) -> None:
        """
        put new user to configuration
        :param user: user descriptor
        :param include_path: path to directory with configuration includes
        """
        target = include_path / "auth.ini"

        configuration = configparser.ConfigParser()
        configuration.read(target)

        section = Configuration.section_name("auth", user.access.value)
        configuration.add_section(section)
        configuration.set(section, user.username, user.password)

        with target.open("w") as ahriman_configuration:
            configuration.write(ahriman_configuration)

    @staticmethod
    def create_user(args: argparse.Namespace, configuration: Configuration) -> User:
        """
        create user descriptor from arguments
        :param args: command line args
        :param configuration: configuration instance
        :return: built user descriptor
        """
        user = User(args.username, args.password, args.role)
        if user.password is None:
            user.password = getpass()
        user.password = user.generate_password(user.password, configuration.get("auth", "salt"))
        return user
