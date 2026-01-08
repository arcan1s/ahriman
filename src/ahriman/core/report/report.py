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
from __future__ import annotations

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import ReportError
from ahriman.core.log import LazyLogging
from ahriman.models.package import Package
from ahriman.models.report_settings import ReportSettings
from ahriman.models.repository_id import RepositoryId
from ahriman.models.result import Result


class Report(LazyLogging):
    """
    base report generator

    Attributes:
        configuration(Configuration): configuration instance
        repository_id(RepositoryId): repository unique identifier

    Examples:
        :class:`Report` subclasses provide several method in order to operate with the report generation and additional
        class method :func:`load()` which can be used in order to determine right report instance::

            >>> configuration = Configuration()
            >>> report = Report.load(RepositoryId("x86_64", "aur"), configuration, "email")

        The :func:`generate()` method can be used in order to perform the report itself, whereas :func:`run()` method
        handles exception and raises :exc:`ahriman.core.exceptions.ReportError` instead::

            >>> try:
            >>>     report.generate([], Result())
            >>> except Exception as exception:
            >>>     handle_exceptions(exception)
            >>>
            >>> report.run(Result(), [])
    """

    def __init__(self, repository_id: RepositoryId, configuration: Configuration) -> None:
        """
        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
        """
        self.repository_id = repository_id
        self.configuration = configuration

    @staticmethod
    def load(repository_id: RepositoryId, configuration: Configuration, target: str) -> Report:  # pylint: disable=too-many-return-statements
        """
        load client from settings

        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            target(str): target to generate report aka section name (e.g. html)

        Returns:
            Report: client according to current settings
        """
        section, provider_name = configuration.gettype(target, repository_id)
        match ReportSettings.from_option(provider_name):
            case ReportSettings.HTML:
                from ahriman.core.report.html import HTML
                return HTML(repository_id, configuration, section)
            case ReportSettings.Email:
                from ahriman.core.report.email import Email
                return Email(repository_id, configuration, section)
            case ReportSettings.Console:
                from ahriman.core.report.console import Console
                return Console(repository_id, configuration, section)
            case ReportSettings.Telegram:
                from ahriman.core.report.telegram import Telegram
                return Telegram(repository_id, configuration, section)
            case ReportSettings.RSS:
                from ahriman.core.report.rss import RSS
                return RSS(repository_id, configuration, section)
            case ReportSettings.RemoteCall:
                from ahriman.core.report.remote_call import RemoteCall
                return RemoteCall(repository_id, configuration, section)
            case _:
                return Report(repository_id, configuration)  # should never happen

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
