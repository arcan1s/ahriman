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
from __future__ import annotations

import logging

from typing import Iterable, Type

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import ReportFailed
from ahriman.models.package import Package
from ahriman.models.report_settings import ReportSettings


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
        self.logger = logging.getLogger("builder")
        self.architecture = architecture
        self.configuration = configuration

    @classmethod
    def load(cls: Type[Report], architecture: str, configuration: Configuration, target: str) -> Report:
        """
        load client from settings
        :param architecture: repository architecture
        :param configuration: configuration instance
        :param target: target to generate report (e.g. html)
        :return: client according to current settings
        """
        provider = ReportSettings.from_option(target)
        if provider == ReportSettings.HTML:
            from ahriman.core.report.html import HTML
            return HTML(architecture, configuration)
        if provider == ReportSettings.Email:
            from ahriman.core.report.email import Email
            return Email(architecture, configuration)
        return cls(architecture, configuration)  # should never happen

    def generate(self, packages: Iterable[Package], built_packages: Iterable[Package]) -> None:
        """
        generate report for the specified packages
        :param packages: list of packages to generate report
        :param built_packages: list of packages which has just been built
        """

    def run(self, packages: Iterable[Package], built_packages: Iterable[Package]) -> None:
        """
        run report generation
        :param packages: list of packages to generate report
        :param built_packages: list of packages which has just been built
        """
        try:
            self.generate(packages, built_packages)
        except Exception:
            self.logger.exception("report generation failed")
            raise ReportFailed()
