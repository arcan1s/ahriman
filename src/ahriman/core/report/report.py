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
from __future__ import annotations

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import ReportError
from ahriman.core.log import LazyLogging
from ahriman.models.package import Package
from ahriman.models.report_settings import ReportSettings
from ahriman.models.result import Result


class Report(LazyLogging):
    """
    base report generator

    Attributes:
        architecture(str): repository architecture
        configuration(Configuration): configuration instance

    Examples:
        ``Report`` classes provide several method in order to operate with the report generation and additional class
        method ``load`` which can be used in order to determine right report instance::

            >>> from ahriman.core.configuration import Configuration
            >>>
            >>> configuration = Configuration()
            >>> report = Report.load("x86_64", configuration, "email")

        The ``generate`` method can be used in order to perform the report itself, whereas ``run`` method handles
        exception and raises ``ReportFailed`` instead::

            >>> try:
            >>>     report.generate([], Result())
            >>> except Exception as exception:
            >>>     handle_exceptions(exception)
            >>>
            >>> report.run(Result(), [])
    """

    def __init__(self, architecture: str, configuration: Configuration) -> None:
        """
        default constructor

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
        """
        self.architecture = architecture
        self.configuration = configuration

    @staticmethod
    def load(architecture: str, configuration: Configuration, target: str) -> Report:
        """
        load client from settings

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            target(str): target to generate report aka section name (e.g. html)

        Returns:
            Report: client according to current settings
        """
        section, provider_name = configuration.gettype(target, architecture)
        match ReportSettings.from_option(provider_name):
            case ReportSettings.HTML:
                from ahriman.core.report.html import HTML
                return HTML(architecture, configuration, section)
            case ReportSettings.Email:
                from ahriman.core.report.email import Email
                return Email(architecture, configuration, section)
            case ReportSettings.Console:
                from ahriman.core.report.console import Console
                return Console(architecture, configuration, section)
            case ReportSettings.Telegram:
                from ahriman.core.report.telegram import Telegram
                return Telegram(architecture, configuration, section)
            case ReportSettings.RemoteCall:
                from ahriman.core.report.remote_call import RemoteCall
                return RemoteCall(architecture, configuration, section)
            case _:
                return Report(architecture, configuration)  # should never happen

    def generate(self, packages: list[Package], result: Result) -> None:
        """
        generate report for the specified packages

        Args:
            packages(list[Package]): list of packages to generate report
            result(Result): build result
        """

    def run(self, result: Result, packages: list[Package]) -> None:
        """
        run report generation

        Args:
            result(Result): build result
            packages(list[Package]): list of packages to generate report

        Raises:
            ReportError: in case of any report unmatched exception
        """
        try:
            self.generate(packages, result)
        except Exception:
            self.logger.exception("report generation failed")
            raise ReportError
