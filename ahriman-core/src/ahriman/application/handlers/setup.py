#
# Copyright (c) 2021-2026 ahriman team.
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
import multiprocessing
import os

from pathlib import Path
from typing import ClassVar
from urllib.parse import quote_plus as url_encode

from ahriman.application.application import Application
from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import InitializeError, MissingArchitectureError
from ahriman.core.utils import enum_values
from ahriman.models.repository_id import RepositoryId
from ahriman.models.sign_settings import SignSettings
from ahriman.models.user import User


class Setup(Handler):
    """
    setup handler

    Attributes:
        MIRRORLIST_PATH(Path): (class attribute) path to pacman default mirrorlist (used by multilib repository)
    """

    ALLOW_MULTI_ARCHITECTURE_RUN = False  # conflicting io

    MIRRORLIST_PATH: ClassVar[Path] = Path("/") / "etc" / "pacman.d" / "mirrorlist"

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
        # special check for args to avoid auto definition for setup command
        if args.architecture is None or args.repository is None:
            raise MissingArchitectureError(args.command)

        target_directory = Setup.configuration_create_directory(configuration)
        Setup.configuration_create_ahriman(args, repository_id, configuration, target_directory)
        configuration.reload()

        application = Application(repository_id, configuration, report=report)
        paths = application.repository.paths

        repository_server = f"file://{paths.repository}" if args.server is None else args.server
        target_directory = paths.ensure_exists(configuration.getpath("build", "devtools_configs"))
        Setup.configuration_create_devtools(repository_id, args.from_configuration, target_directory, args.mirror,
                                            args.multilib, repository_server)

        # finish initialization
        with paths.preserve_owner():
            application.repository.repo.init()
            # lazy database sync
            application.repository.pacman.handle  # pylint: disable=pointless-statement

    @staticmethod
    def _set_service_setup_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for setup subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("service-setup", aliases=["init", "repo-init", "repo-setup", "setup"],
                                 help="initial service configuration",
                                 description="create initial service configuration as the repository owner",
                                 epilog="Create minimal configuration for the service according to provided options.")
        parser.add_argument("--build-as-user", help="force makepkg user to the specific one")
        parser.add_argument("--from-configuration", help="path to default devtools pacman configuration",
                            type=Path,
                            default=Path("/") / "usr" / "share" / "devtools" / "pacman.conf.d" / "extra.conf")
        parser.add_argument("--generate-salt", help="generate salt for user passwords",
                            action=argparse.BooleanOptionalAction, default=False)
        parser.add_argument("--makeflags-jobs",
                            help="append MAKEFLAGS variable with parallelism set to number of cores",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("--mirror", help="use the specified explicitly mirror instead of including mirrorlist")
        parser.add_argument("--multilib", help="add or do not multilib repository",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("--packager", help="packager name and email", required=True)
        parser.add_argument("--server", help="server to be used for devtools. If none set, local files will be used")
        parser.add_argument("--sign-key", help="sign key id")
        parser.add_argument("--sign-target", help="sign options", action="append",
                            type=SignSettings.from_option, choices=enum_values(SignSettings))
        parser.add_argument("--web-port", help="port of the web service", type=int)
        parser.add_argument("--web-unix-socket", help="path to unix socket used for interprocess communications",
                            type=Path)
        parser.set_defaults(lock=None, quiet=True, report=False)
        return parser

    @staticmethod
    def configuration_create_ahriman(args: argparse.Namespace, repository_id: RepositoryId,
                                     root: Configuration, target_directory: Path) -> None:
        """
        create service specific configuration

        Args:
            args(argparse.Namespace): command line args
            repository_id(RepositoryId): repository unique identifier
            root(Configuration): root configuration instance
            target_directory(Path): path to directory where configuration files will be written
        """
        configuration = Configuration()

        configuration.set_option("repository", "name", repository_id.name)  # backward compatibility for docker

        section = Configuration.section_name("build", repository_id.name, repository_id.architecture)
        configuration.set_option(section, "packager", args.packager)
        if args.makeflags_jobs:
            configuration.set_option(section, "make_flags", f"-j{multiprocessing.cpu_count()}")
        if args.build_as_user is not None:
            configuration.set_option(section, "makechrootpkg_flags", f"-U {args.build_as_user}")

        section = Configuration.section_name("alpm", repository_id.name, repository_id.architecture)
        if args.mirror is not None:
            configuration.set_option(section, "mirror", args.mirror)
        if not args.multilib:
            repositories = filter(lambda r: r != "multilib", root.getlist("alpm", "repositories"))
            configuration.set_option(section, "repositories", " ".join(repositories))

        section = Configuration.section_name("sign", repository_id.name, repository_id.architecture)
        if args.sign_key is not None:
            sign_targets = args.sign_target or []
            configuration.set_option(section, "target", " ".join([target.name.lower() for target in sign_targets]))
            configuration.set_option(section, "key", args.sign_key)

        if args.web_port is not None:
            configuration.set_option("web", "port", str(args.web_port))
            if (host := root.get("web", "host", fallback=None)) is not None:
                configuration.set_option("status", "address", f"http://{host}:{args.web_port}")
        if args.web_unix_socket is not None:
            unix_socket = str(args.web_unix_socket)
            configuration.set_option("web", "unix_socket", unix_socket)
            configuration.set_option("status", "address", f"http+unix://{url_encode(unix_socket)}")

        if args.generate_salt:
            configuration.set_option("auth", "salt", User.generate_password(20))

        target = target_directory / f"00-setup-overrides-{repository_id.id}.ini"
        with target.open("w", encoding="utf8") as ahriman_configuration:
            configuration.write(ahriman_configuration)

    @staticmethod
    def configuration_create_devtools(repository_id: RepositoryId, source: Path, target_directory: Path,
                                      mirror: str | None, multilib: bool, repository_server: str) -> None:
        """
        create configuration for devtools based on ``source`` configuration

        Notes:
            devtools does not allow to specify the pacman configuration, thus we still have to use configuration in /usr

        Args:
            repository_id(RepositoryId): repository unique identifier
            source(Path): path to source configuration file
            target_directory(Path): path to directory where configuration files will be written
            mirror(str | None): link to package server mirror
            multilib(bool): add or do not multilib repository to the configuration
            repository_server(str): url of the repository
        """
        # allow_no_value=True is required because pacman uses boolean configuration in which just keys present
        # (e.g. NoProgressBar) which will lead to exception. allow_multi_key=False is set just for fun
        configuration = Configuration(allow_no_value=True, allow_multi_key=False)
        # preserve case
        # stupid mypy thinks that it is impossible
        configuration.optionxform = lambda optionstr: optionstr  # type: ignore[method-assign]

        # load default configuration first
        # we cannot use Include here because it will be copied to new chroot, thus no includes there
        configuration.read(source)

        # set our architecture now
        configuration.set_option("options", "Architecture", repository_id.architecture)

        # add multilib
        if multilib:
            configuration.set_option("multilib", "Include", str(Setup.MIRRORLIST_PATH))

        # override Include option to Server in case if mirror option set
        if mirror is not None:
            for section in filter(lambda s: s != "options", configuration.sections()):
                if configuration.get(section, "Include", fallback=None) != str(Setup.MIRRORLIST_PATH):
                    continue
                configuration.remove_option(section, "Include")
                configuration.set_option(section, "Server", mirror)

        # add repository itself
        configuration.set_option(repository_id.name, "SigLevel", "Never")  # we don't care
        configuration.set_option(repository_id.name, "Server", repository_server)

        target = target_directory / f"{repository_id.name}-{repository_id.architecture}.conf"
        with target.open("w", encoding="utf8") as devtools_configuration:
            configuration.write(devtools_configuration)

    @staticmethod
    def configuration_create_directory(root: Configuration) -> Path:
        """
        create directory for includes

        Args:
            root(Configuration): root configuration instance

        Returns:
            Path: path to first writable directory

        Raises:
            InitializeError: if no writable directories have been found
        """
        for include_path in root.include:
            try:
                directory = root.repository_paths.ensure_exists(include_path)
                if os.access(directory, os.W_OK | os.X_OK):
                    return directory
            except OSError:
                continue

        raise InitializeError("No writable include directory found")

    arguments = [_set_service_setup_parser]
