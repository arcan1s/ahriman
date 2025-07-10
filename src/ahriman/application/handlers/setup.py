#
# Copyright (c) 2021-2025 ahriman team.
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
from pwd import getpwuid
from typing import ClassVar
from urllib.parse import quote_plus as url_encode

from ahriman.application.application import Application
from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import MissingArchitectureError
from ahriman.core.utils import enum_values
from ahriman.models.repository_id import RepositoryId
from ahriman.models.repository_paths import RepositoryPaths
from ahriman.models.sign_settings import SignSettings
from ahriman.models.user import User


class Setup(Handler):
    """
    setup handler

    Attributes:
        ARCHBUILD_COMMAND_PATH(Path): (class attribute) default devtools command
        MIRRORLIST_PATH(Path): (class attribute) path to pacman default mirrorlist (used by multilib repository)
        SUDOERS_DIR_PATH(Path): (class attribute) path to sudoers.d includes directory
    """

    ALLOW_MULTI_ARCHITECTURE_RUN = False  # conflicting io

    ARCHBUILD_COMMAND_PATH: ClassVar[Path] = Path("/") / "usr" / "bin" / "archbuild"
    MIRRORLIST_PATH: ClassVar[Path] = Path("/") / "etc" / "pacman.d" / "mirrorlist"
    SUDOERS_DIR_PATH: ClassVar[Path] = Path("/") / "etc" / "sudoers.d"

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

        Setup.configuration_create_ahriman(args, repository_id, configuration)
        configuration.reload()

        application = Application(repository_id, configuration, report=report)

        with application.repository.paths.preserve_owner():
            Setup.configuration_create_makepkg(args.packager, args.makeflags_jobs, application.repository.paths)
            Setup.executable_create(application.repository.paths, repository_id)
            repository_server = f"file://{application.repository.paths.repository}" if args.server is None else args.server
            Setup.configuration_create_devtools(
                repository_id, args.from_configuration, args.mirror, args.multilib, repository_server)
            Setup.configuration_create_sudo(application.repository.paths, repository_id)

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
                                 description="create initial service configuration, requires root",
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
        parser.set_defaults(lock=None, quiet=True, report=False, unsafe=True)
        return parser

    @staticmethod
    def build_command(root: Path, repository_id: RepositoryId) -> Path:
        """
        generate build command name

        Args:
            root(Path): root directory for the build command (must be root of the repository)
            repository_id(RepositoryId): repository unique identifier

        Returns:
            Path: valid devtools command name
        """
        return root / f"{repository_id.name}-{repository_id.architecture}-build"

    @staticmethod
    def configuration_create_ahriman(args: argparse.Namespace, repository_id: RepositoryId,
                                     root: Configuration) -> None:
        """
        create service specific configuration

        Args:
            args(argparse.Namespace): command line args
            repository_id(RepositoryId): repository unique identifier
            root(Configuration): root configuration instance
        """
        configuration = Configuration()

        section = Configuration.section_name("build", repository_id.name, repository_id.architecture)
        build_command = Setup.build_command(root.repository_paths.root, repository_id)
        configuration.set_option(section, "build_command", str(build_command))
        configuration.set_option("repository", "name", repository_id.name)  # backward compatibility for docker
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

        (root.include / "00-setup-overrides.ini").unlink(missing_ok=True)  # remove old-style configuration
        target = root.include / f"00-setup-overrides-{repository_id.id}.ini"
        with target.open("w", encoding="utf8") as ahriman_configuration:
            configuration.write(ahriman_configuration)

    @staticmethod
    def configuration_create_devtools(repository_id: RepositoryId, source: Path, mirror: str | None,
                                      multilib: bool, repository_server: str) -> None:
        """
        create configuration for devtools based on ``source`` configuration

        Notes:
            devtools does not allow to specify the pacman configuration, thus we still have to use configuration in /usr

        Args:
            repository_id(RepositoryId): repository unique identifier
            source(Path): path to source configuration file
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

        target = source.parent / f"{repository_id.name}-{repository_id.architecture}.conf"
        with target.open("w", encoding="utf8") as devtools_configuration:
            configuration.write(devtools_configuration)

    @staticmethod
    def configuration_create_makepkg(packager: str, makeflags_jobs: bool, paths: RepositoryPaths) -> None:
        """
        create configuration for makepkg

        Args:
            packager(str): packager identifier (e.g. name, email)
            makeflags_jobs(bool): set MAKEFLAGS variable to number of cores
            paths(RepositoryPaths): repository paths instance
        """

        content = f"PACKAGER='{packager}'\n"
        if makeflags_jobs:
            content += """MAKEFLAGS="-j$(nproc)"\n"""

        uid, _ = paths.root_owner
        home_dir = Path(getpwuid(uid).pw_dir)
        (home_dir / ".makepkg.conf").write_text(content, encoding="utf8")

    @staticmethod
    def configuration_create_sudo(paths: RepositoryPaths, repository_id: RepositoryId) -> None:
        """
        create configuration to run build command with sudo without password

        Args:
            paths(RepositoryPaths): repository paths instance
            repository_id(RepositoryId): repository unique identifier
        """
        command = Setup.build_command(paths.root, repository_id)
        sudoers_file = Setup.build_command(Setup.SUDOERS_DIR_PATH, repository_id)
        sudoers_file.write_text(f"ahriman ALL=(ALL) NOPASSWD:SETENV: {command} *\n", encoding="utf8")
        sudoers_file.chmod(0o400)  # security!

    @staticmethod
    def executable_create(paths: RepositoryPaths, repository_id: RepositoryId) -> None:
        """
        create executable for the service

        Args:
            paths(RepositoryPaths): repository paths instance
            repository_id(RepositoryId): repository unique identifier
        """
        command = Setup.build_command(paths.root, repository_id)
        command.unlink(missing_ok=True)
        command.symlink_to(Setup.ARCHBUILD_COMMAND_PATH)

    arguments = [_set_service_setup_parser]
