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
import datetime

from collections.abc import Callable
from email.utils import format_datetime, parsedate_to_datetime
from typing import Any

from ahriman.core import context
from ahriman.core.configuration import Configuration
from ahriman.core.report.jinja_template import JinjaTemplate
from ahriman.core.report.report import Report
from ahriman.core.status import Client
from ahriman.models.event import EventType
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId
from ahriman.models.result import Result


class RSS(Report, JinjaTemplate):
    """
    RSS report generator

    Attributes:
        max_entries(int): the maximal amount of entries in RSS
        report_path(Path): output path to RSS report
        template(str): name of the template
    """

    def __init__(self, repository_id: RepositoryId, configuration: Configuration, section: str) -> None:
        """
        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            section(str): settings section name
        """
        Report.__init__(self, repository_id, configuration)
        JinjaTemplate.__init__(self, repository_id, configuration, section)

        self.max_entries = configuration.getint(section, "max_entries", fallback=-1)
        self.report_path = configuration.getpath(section, "path")
        self.template = configuration.get(section, "template")

    @staticmethod
    def format_datetime(timestamp: datetime.datetime | float | int | None) -> str:
        """
        convert datetime object to string

        Args:
            timestamp(datetime.datetime | float | int | None): datetime to convert

        Returns:
            str: datetime as string representation
        """
        if timestamp is None:
            return ""
        if isinstance(timestamp, (int, float)):
            timestamp = datetime.datetime.fromtimestamp(timestamp, datetime.UTC)
        return format_datetime(timestamp)

    @staticmethod
    def sort_content(content: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        sort content before rendering

        Args:
            content(list[dict[str, str]]): content of the template

        Returns:
            list[dict[str, str]]: sorted content according to comparator defined
        """
        comparator: Callable[[dict[str, str]], datetime.datetime] = \
            lambda item: parsedate_to_datetime(item["build_date"])
        return sorted(content, key=comparator, reverse=True)

    def content(self, packages: list[Package]) -> Result:
        """
        extract result to be written to template

        Args:
            packages(list[Package]): list of packages to generate report

        Returns:
            Result: result descriptor
        """
        ctx = context.get()
        reporter = ctx.get(Client)
        events = reporter.event_get(EventType.PackageUpdated, None, limit=self.max_entries)

        known_packages = {package.base: package for package in packages}

        result = Result()
        for event in events:
            package = known_packages.get(event.object_id)
            if package is None:
                continue  # package not found
            result.add_updated(package)

        return result

    def generate(self, packages: list[Package], result: Result) -> None:
        """
        generate report for the specified packages

        Args:
            packages(list[Package]): list of packages to generate report
            result(Result): build result
        """
        result = self.content(packages)
        rss = self.make_html(result, self.template)
        self.report_path.write_text(rss, encoding="utf8")
