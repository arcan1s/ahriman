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

from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.core.formatters import ConfigurationPathsPrinter, ConfigurationPrinter, StringPrinter
from ahriman.models.repository_id import RepositoryId


class Dump(Handler):
    """
    dump configuration handler
    """

    ALLOW_MULTI_ARCHITECTURE_RUN = False  # conflicting io

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
        if args.info:
            root, _ = configuration.check_loaded()
            ConfigurationPathsPrinter(root, configuration.includes)(verbose=True, separator=" = ")

        match (args.section, args.key):
            case None, None:  # full configuration
                dump = configuration.dump()
                for section, values in sorted(dump.items()):
                    ConfigurationPrinter(section, values)(verbose=not args.secure, separator=" = ")
            case section, None:  # section only
                values = dict(configuration.items(section)) if configuration.has_section(section) else {}
                ConfigurationPrinter(section, values)(verbose=not args.secure, separator=" = ")
            case section, key:  # key only
                value = configuration.get(section, key, fallback="")
                StringPrinter(value)(verbose=False)

    @staticmethod
    def _set_service_config_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for config subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("service-config", aliases=["config", "repo-config"], help="dump configuration",
                                 description="dump configuration for the specified architecture")
        parser.add_argument("section", help="filter settings by section", nargs="?")
        parser.add_argument("key", help="filter settings by key", nargs="?")
        parser.add_argument("--info", help="show additional information, e.g. configuration files",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("--secure", help="hide passwords and secrets from output",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.set_defaults(lock=None, quiet=True, report=False, unsafe=True)
        return parser

    arguments = [_set_service_config_parser]
