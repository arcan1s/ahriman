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

from collections.abc import Callable

from ahriman.application.application import Application
from ahriman.application.handlers import Handler
from ahriman.core.configuration import Configuration
from ahriman.core.formatters import PackagePrinter, StatusPrinter
from ahriman.models.build_status import BuildStatus
from ahriman.models.package import Package


class Status(Handler):
    """
    package status handler
    """

    ALLOW_AUTO_ARCHITECTURE_RUN = False

    @classmethod
    def run(cls, args: argparse.Namespace, architecture: str, configuration: Configuration, *,
            report: bool, unsafe: bool) -> None:
        """
        callback for command line

        Args:
            args(argparse.Namespace): command line args
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting
            unsafe(bool): if set no user check will be performed before path creation
        """
        # we are using reporter here
        client = Application(architecture, configuration, report=True, unsafe=unsafe).repository.reporter
        if args.ahriman:
            service_status = client.get_internal()
            StatusPrinter(service_status.status).print(verbose=args.info)
        if args.package:
            packages: list[tuple[Package, BuildStatus]] = sum(
                (client.get(base) for base in args.package),
                start=[])
        else:
            packages = client.get(None)

        Status.check_if_empty(args.exit_code, not packages)

        comparator: Callable[[tuple[Package, BuildStatus]], str] = lambda item: item[0].base
        filter_fn: Callable[[tuple[Package, BuildStatus]], bool] =\
            lambda item: args.status is None or item[1].status == args.status
        for package, package_status in sorted(filter(filter_fn, packages), key=comparator):
            PackagePrinter(package, package_status).print(verbose=args.info)
