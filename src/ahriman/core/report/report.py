#
# Copyright (c) 2021-2022 ahriman team.
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

import logging

from typing import Iterable, Type

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import ReportFailed
from ahriman.models.package import Package
from ahriman.models.report_settings import ReportSettings
from ahriman.models.result import Result


class Report:
    """
    base report generator
    :ivar architecture: repository architecture
    :ivar configuration: configuration instance
    :ivar logger: class logger
    """

    def __init__(self, architecture: str, configuration: Configuration) -> None:
        """
        default constructor
        :param architecture: repository architecture
        :param configuration: configuration instance
        """
        self.logger = logging.getLogger("root")
        self.architecture = architecture
        self.configuration = configuration

    @classmethod
    def load(cls: Type[Report], architecture: str, configuration: Configuration, target: str) -> Report:
        """
        load client from settings
        :param architecture: repository architecture
        :param configuration: configuration instance
        :param target: target to generate report aka section name (e.g. html)
        :return: client according to current settings
        """
        section, provider_name = configuration.gettype(target, architecture)
        provider = ReportSettings.from_option(provider_name)
        if provider == ReportSettings.HTML:
            from ahriman.core.report.html import HTML
            return HTML(architecture, configuration, section)
        if provider == ReportSettings.Email:
            from ahriman.core.report.email import Email
            return Email(architecture, configuration, section)
        if provider == ReportSettings.Console:
            from ahriman.core.report.console import Console
            return Console(architecture, configuration, section)
        if provider == ReportSettings.Telegram:
            from ahriman.core.report.telegram import Telegram
            return Telegram(architecture, configuration, section)
        return cls(architecture, configuration)  # should never happen

    def generate(self, packages: Iterable[Package], result: Result) -> None:
        """
        generate report for the specified packages
        :param packages: list of packages to generate report
        :param result: build result
        """

    def run(self, packages: Iterable[Package], result: Result) -> None:
        """
        run report generation
        :param packages: list of packages to generate report
        :param result: build result
        """
        try:
            self.generate(packages, result)
        except Exception:
            self.logger.exception("report generation failed")
            raise ReportFailed()
