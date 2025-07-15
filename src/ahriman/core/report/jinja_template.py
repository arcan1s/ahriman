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
import jinja2

from collections.abc import Callable
from pathlib import Path
from typing import Any

from ahriman.core.configuration import Configuration
from ahriman.core.sign.gpg import GPG
from ahriman.core.types import Comparable
from ahriman.core.utils import pretty_datetime, pretty_size, utcnow
from ahriman.models.repository_id import RepositoryId
from ahriman.models.result import Result
from ahriman.models.sign_settings import SignSettings


class JinjaTemplate:
    """
    jinja based report generator

    It uses jinja2 templates for report generation, the following variables are allowed:

        * homepage - link to homepage, string, optional
        * last_update - report generation time, pretty printed datetime, required
        * link_path - prefix of packages to download, string, required
        * has_package_signed - ``True`` in case if package sign enabled, ``False`` otherwise, required
        * has_repo_signed - ``True`` in case if repository database sign enabled, ``False`` otherwise, required
        * packages - sorted list of packages properties, required
            * architecture, string
            * archive_size, pretty printed size, string
            * build_date, pretty printed datetime, string
            * depends, sorted list of strings
            * description, string
            * filename, string
            * groups, sorted list of strings
            * installed_size, pretty printed size, string
            * licenses, sorted list of strings
            * name, string
            * tag, string
            * url, string
            * version, string
        * pgp_key - default PGP key ID, string, optional
        * repository - repository name, string, required
        * rss_url - optional link to the RSS feed, string, optional

    Attributes:
        default_pgp_key(str | None): default PGP key
        homepage(str | None): homepage link if any (for footer)
        link_path(str): prefix of packages to download
        name(str): repository name
        rss_url(str | None): link to the RSS feed
        sign_targets(set[SignSettings]): targets to sign enabled in configuration
        templates(list[Path]): list of directories with templates
    """

    def __init__(self, repository_id: RepositoryId, configuration: Configuration, section: str) -> None:
        """
        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            section(str): settings section name
        """
        self.templates = configuration.getpathlist(section, "templates", fallback=[])

        # base template vars
        self.homepage = configuration.get(section, "homepage", fallback=None)
        self.link_path = configuration.get(section, "link_path")
        self.name = repository_id.name
        self.rss_url = configuration.get(section, "rss_url", fallback=None)
        self.sign_targets, self.default_pgp_key = GPG.sign_options(configuration)

    @staticmethod
    def format_datetime(timestamp: datetime.datetime | float | int | None) -> str:
        """
        convert datetime object to string

        Args:
            timestamp(datetime.datetime | float | int | None): datetime to convert

        Returns:
            str: datetime as string representation
        """
        return pretty_datetime(timestamp)

    @staticmethod
    def sort_content(content: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        sort content before rendering

        Args:
            content(list[dict[str, str]]): content of the template

        Returns:
            list[dict[str, str]]: sorted content according to comparator defined
        """
        comparator: Callable[[dict[str, str]], Comparable] = lambda item: item["filename"]
        return sorted(content, key=comparator)

    def make_html(self, result: Result, template_name: Path | str) -> str:
        """
        generate report for the specified packages

        Args:
            result(Result): build result
            template_name(Path | str): name of the template or path to it (legacy configuration)
        """
        templates = self.templates[:]
        if isinstance(template_name, Path):
            templates.append(template_name.parent)
            template_name = template_name.name

        # idea comes from https://stackoverflow.com/a/38642558
        loader = jinja2.FileSystemLoader(searchpath=templates)
        environment = jinja2.Environment(trim_blocks=True, lstrip_blocks=True, autoescape=True, loader=loader)
        template = environment.get_template(template_name)

        content = [
            {
                "architecture": properties.architecture or "",
                "archive_size": pretty_size(properties.archive_size),
                "build_date": self.format_datetime(properties.build_date),
                "depends": properties.depends,
                "description": properties.description or "",
                "filename": properties.filename,
                "groups": properties.groups,
                "installed_size": pretty_size(properties.installed_size),
                "licenses": properties.licenses,
                "name": package,
                "tag": f"tag:{self.name}:{properties.architecture}:{package}:{base.version}:{properties.build_date}",
                "url": properties.url or "",
                "version": base.version,
            } for base in result.success for package, properties in base.packages.items()
        ]

        return template.render(
            homepage=self.homepage,
            last_update=self.format_datetime(utcnow()),
            link_path=self.link_path,
            has_package_signed=SignSettings.Packages in self.sign_targets,
            has_repo_signed=SignSettings.Repository in self.sign_targets,
            packages=self.sort_content(content),
            pgp_key=self.default_pgp_key,
            repository=self.name,
            rss_url=self.rss_url,
        )
