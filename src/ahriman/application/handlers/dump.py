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

from ahriman.application.handlers import Handler
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
        root, _ = configuration.check_loaded()
        ConfigurationPathsPrinter(root, configuration.includes)(verbose=True, separator=" = ")

        # empty line
        StringPrinter("")(verbose=False)

        dump = configuration.dump()
        for section, values in sorted(dump.items()):
            ConfigurationPrinter(section, values)(verbose=not args.secure, separator=" = ")
