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

from pathlib import Path
from typing import Type

from ahriman.application.application import Application
from ahriman.application.handlers.handler import Handler
from ahriman.core.configuration import Configuration
from ahriman.models.repository_paths import RepositoryPaths


class Setup(Handler):
    """
    setup handler
    :cvar ARCHBUILD_COMMAND_PATH: default devtools command
    :cvar BIN_DIR_PATH: directory for custom binaries
    :cvar MIRRORLIST_PATH: path to pacman default mirrorlist (used by multilib repository)
    :cvar SUDOERS_PATH: path to sudoers.d include configuration
    """

    ARCHBUILD_COMMAND_PATH = Path("/usr/bin/archbuild")
    BIN_DIR_PATH = Path("/usr/local/bin")
    MIRRORLIST_PATH = Path("/etc/pacman.d/mirrorlist")
    SUDOERS_PATH = Path("/etc/sudoers.d/ahriman")

    @classmethod
    def run(cls: Type[Handler], args: argparse.Namespace, architecture: str, configuration: Configuration) -> None:
        """
        callback for command line
        :param args: command line args
        :param architecture: repository architecture
        :param configuration: configuration instance
        """
        application = Application(architecture, configuration)
        Setup.create_makepkg_configuration(args.packager, application.repository.paths)
        Setup.create_executable(args.build_command, architecture)
        Setup.create_devtools_configuration(args.build_command, architecture, Path(args.from_configuration),
                                            args.no_multilib, args.repository, application.repository.paths)
        Setup.create_ahriman_configuration(args, architecture, args.repository, configuration.include)
        Setup.create_sudo_configuration(args.build_command, architecture)

    @staticmethod
    def build_command(prefix: str, architecture: str) -> Path:
        """
        generate build command name
        :param prefix: command prefix in {prefix}-{architecture}-build
        :param architecture: repository architecture
        :return: valid devtools command name
        """
        return Setup.BIN_DIR_PATH / f"{prefix}-{architecture}-build"

    @staticmethod
    def create_ahriman_configuration(args: argparse.Namespace, architecture: str, repository: str,
                                     include_path: Path) -> None:
        """
        create service specific configuration
        :param args: command line args
        :param architecture: repository architecture
        :param repository: repository name
        :param include_path: path to directory with configuration includes
        """
        configuration = configparser.ConfigParser()

        section = Configuration.section_name("build", architecture)
        configuration.add_section(section)
        configuration.set(section, "build_command", str(Setup.build_command(args.build_command, architecture)))

        configuration.add_section("repository")
        configuration.set("repository", "name", repository)

        if args.sign_key is not None:
            section = Configuration.section_name("sign", architecture)
            configuration.add_section(section)
            configuration.set(section, "target", " ".join(args.sign_target))
            configuration.set(section, "key", args.sign_key)

        if args.web_port is not None:
            section = Configuration.section_name("web", architecture)
            configuration.add_section(section)
            configuration.set(section, "port", str(args.web_port))

        target = include_path / "setup-overrides.ini"
        with target.open("w") as ahriman_configuration:
            configuration.write(ahriman_configuration)

    @staticmethod
    def create_devtools_configuration(prefix: str, architecture: str, source: Path,
                                      no_multilib: bool, repository: str, paths: RepositoryPaths) -> None:
        """
        create configuration for devtools based on `source` configuration
        :param prefix: command prefix in {prefix}-{architecture}-build
        :param architecture: repository architecture
        :param source: path to source configuration file
        :param no_multilib: do not add multilib repository
        :param repository: repository name
        :param paths: repository paths instance
        """
        configuration = configparser.ConfigParser()
        # preserve case
        # stupid mypy thinks that it is impossible
        configuration.optionxform = lambda key: key  # type: ignore

        # load default configuration first
        # we cannot use Include here because it will be copied to new chroot, thus no includes there
        configuration.read(source)

        # set our architecture now
        configuration.set("options", "Architecture", architecture)

        # add multilib
        if not no_multilib:
            configuration.add_section("multilib")
            configuration.set("multilib", "Include", str(Setup.MIRRORLIST_PATH))

        # add repository itself
        configuration.add_section(repository)
        configuration.set(repository, "SigLevel", "Optional TrustAll")  # we don't care
        configuration.set(repository, "Server", f"file://{paths.repository}")

        target = source.parent / f"pacman-{prefix}-{architecture}.conf"
        with target.open("w") as devtools_configuration:
            configuration.write(devtools_configuration)

    @staticmethod
    def create_makepkg_configuration(packager: str, paths: RepositoryPaths) -> None:
        """
        create configuration for makepkg
        :param packager: packager identifier (e.g. name, email)
        :param paths: repository paths instance
        """
        (paths.root / ".makepkg.conf").write_text(f"PACKAGER='{packager}'\n")

    @staticmethod
    def create_sudo_configuration(prefix: str, architecture: str) -> None:
        """
        create configuration to run build command with sudo without password
        :param prefix: command prefix in {prefix}-{architecture}-build
        :param architecture: repository architecture
        """
        command = Setup.build_command(prefix, architecture)
        Setup.SUDOERS_PATH.write_text(f"ahriman ALL=(ALL) NOPASSWD: {command} *\n")
        Setup.SUDOERS_PATH.chmod(0o400)  # security!

    @staticmethod
    def create_executable(prefix: str, architecture: str) -> None:
        """
        create executable for the service
        :param prefix: command prefix in {prefix}-{architecture}-build
        :param architecture: repository architecture
        """
        command = Setup.build_command(prefix, architecture)
        command.unlink(missing_ok=True)
        command.symlink_to(Setup.ARCHBUILD_COMMAND_PATH)
