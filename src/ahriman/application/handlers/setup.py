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

    ALLOW_AUTO_ARCHITECTURE_RUN = False

    ARCHBUILD_COMMAND_PATH = Path("/usr/bin/archbuild")
    BIN_DIR_PATH = Path("/usr/local/bin")
    MIRRORLIST_PATH = Path("/etc/pacman.d/mirrorlist")
    SUDOERS_PATH = Path("/etc/sudoers.d/ahriman")

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
        application = Application(architecture, configuration, no_report, unsafe)
        Setup.configuration_create_makepkg(args.packager, application.repository.paths)
        Setup.executable_create(args.build_command, architecture)
        Setup.configuration_create_devtools(args.build_command, architecture, args.from_configuration,
                                            args.no_multilib, args.repository, application.repository.paths)
        Setup.configuration_create_ahriman(args, architecture, args.repository, configuration.include)
        Setup.configuration_create_sudo(args.build_command, architecture)

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
    def configuration_create_ahriman(args: argparse.Namespace, architecture: str, repository: str,
                                     include_path: Path) -> None:
        """
        create service specific configuration
        :param args: command line args
        :param architecture: repository architecture
        :param repository: repository name
        :param include_path: path to directory with configuration includes
        """
        configuration = Configuration()

        section = Configuration.section_name("build", architecture)
        configuration.set_option(section, "build_command", str(Setup.build_command(args.build_command, architecture)))
        configuration.set_option("repository", "name", repository)
        if args.build_as_user is not None:
            configuration.set_option(section, "makechrootpkg_flags", f"-U {args.build_as_user}")

        if args.sign_key is not None:
            section = Configuration.section_name("sign", architecture)
            configuration.set_option(section, "target", " ".join([target.name.lower() for target in args.sign_target]))
            configuration.set_option(section, "key", args.sign_key)

        if args.web_port is not None:
            section = Configuration.section_name("web", architecture)
            configuration.set_option(section, "port", str(args.web_port))

        target = include_path / "setup-overrides.ini"
        with target.open("w") as ahriman_configuration:
            configuration.write(ahriman_configuration)

    @staticmethod
    def configuration_create_devtools(prefix: str, architecture: str, source: Path,
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
        configuration = Configuration()
        # preserve case
        # stupid mypy thinks that it is impossible
        configuration.optionxform = lambda key: key  # type: ignore

        # load default configuration first
        # we cannot use Include here because it will be copied to new chroot, thus no includes there
        configuration.read(source)

        # set our architecture now
        configuration.set_option("options", "Architecture", architecture)

        # add multilib
        if not no_multilib:
            configuration.set_option("multilib", "Include", str(Setup.MIRRORLIST_PATH))

        # add repository itself
        configuration.set_option(repository, "SigLevel", "Optional TrustAll")  # we don't care
        configuration.set_option(repository, "Server", f"file://{paths.repository}")

        target = source.parent / f"pacman-{prefix}-{architecture}.conf"
        with target.open("w") as devtools_configuration:
            configuration.write(devtools_configuration)

    @staticmethod
    def configuration_create_makepkg(packager: str, paths: RepositoryPaths) -> None:
        """
        create configuration for makepkg
        :param packager: packager identifier (e.g. name, email)
        :param paths: repository paths instance
        """
        (paths.root / ".makepkg.conf").write_text(f"PACKAGER='{packager}'\n", encoding="utf8")

    @staticmethod
    def configuration_create_sudo(prefix: str, architecture: str) -> None:
        """
        create configuration to run build command with sudo without password
        :param prefix: command prefix in {prefix}-{architecture}-build
        :param architecture: repository architecture
        """
        command = Setup.build_command(prefix, architecture)
        Setup.SUDOERS_PATH.write_text(f"ahriman ALL=(ALL) NOPASSWD: {command} *\n", encoding="utf8")
        Setup.SUDOERS_PATH.chmod(0o400)  # security!

    @staticmethod
    def executable_create(prefix: str, architecture: str) -> None:
        """
        create executable for the service
        :param prefix: command prefix in {prefix}-{architecture}-build
        :param architecture: repository architecture
        """
        command = Setup.build_command(prefix, architecture)
        command.unlink(missing_ok=True)
        command.symlink_to(Setup.ARCHBUILD_COMMAND_PATH)
