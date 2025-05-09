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
from ahriman.core.configuration import Configuration
from ahriman.core.report.jinja_template import JinjaTemplate
from ahriman.core.report.report import Report
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId
from ahriman.models.result import Result


class HTML(Report, JinjaTemplate):
    """
    html report generator

    Attributes:
        report_path(Path): output path to html report
        template(Path | str): name or path to template for full package list
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

        self.report_path = configuration.getpath(section, "path")
        self.template = configuration.get(section, "template", fallback=None) or \
            configuration.getpath(section, "template_path")

    def generate(self, packages: list[Package], result: Result) -> None:
        """
        generate report for the specified packages

        Args:
            packages(list[Package]): list of packages to generate report
            result(Result): build result
        """
        html = self.make_html(Result(updated=packages), self.template)
        self.report_path.write_text(html, encoding="utf8")
