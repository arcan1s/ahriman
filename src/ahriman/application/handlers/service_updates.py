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

from ahriman import __version__
from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.core.formatters import UpdatePrinter
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId


class ServiceUpdates(Handler):
    """
    service updates handler
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
        remote = Package.from_aur("ahriman", None)
        _, release = remote.version.rsplit("-", maxsplit=1)  # we don't store pkgrel locally, so we just append it
        local_version = f"{__version__}-{release}"

        # technically we would like to compare versions, but it is fine to raise an exception in case if locally
        # installed package is newer than in AUR
        same_version = remote.version == local_version
        if same_version:
            return

        UpdatePrinter(remote, local_version)(verbose=True, separator=" -> ")
        ServiceUpdates.check_status(args.exit_code, same_version)

    @staticmethod
    def _set_help_updates_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for service update check subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("help-updates", help="check for service updates",
                                 description="request AUR for current version and compare with current service version")
        parser.add_argument("-e", "--exit-code", help="return non-zero exit code if updates available",
                            action="store_true")
        parser.set_defaults(architecture="", lock=None, quiet=True, report=False, repository="", unsafe=True)
        return parser

    arguments = [_set_help_updates_parser]
