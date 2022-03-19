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
import jinja2

from pathlib import Path
from typing import Callable, Dict

from ahriman.core.configuration import Configuration
from ahriman.core.sign.gpg import GPG
from ahriman.core.util import pretty_datetime, pretty_size
from ahriman.models.result import Result
from ahriman.models.sign_settings import SignSettings


class JinjaTemplate:
    """
    jinja based report generator

    It uses jinja2 templates for report generation, the following variables are allowed:

        homepage - link to homepage, string, optional
        link_path - prefix fo packages to download, string, required
        has_package_signed - True in case if package sign enabled, False otherwise, required
        has_repo_signed - True in case if repository database sign enabled, False otherwise, required
        packages - sorted list of packages properties, required
                   * architecture, string
                   * archive_size, pretty printed size, string
                   * build_date, pretty printed datetime, string
                   * depends, sorted list of strings
                   * description, string
                   * filename, string,
                   * groups, sorted list of strings
                   * installed_size, pretty printed datetime, string
                   * licenses, sorted list of strings
                   * name, string
                   * url, string
                   * version, string
        pgp_key - default PGP key ID, string, optional
        repository - repository name, string, required

    :ivar homepage: homepage link if any (for footer)
    :ivar link_path: prefix fo packages to download
    :ivar name: repository name
    :ivar default_pgp_key: default PGP key
    :ivar sign_targets: targets to sign enabled in configuration
    """

    def __init__(self, section: str, configuration: Configuration) -> None:
        """
        default constructor
        :param section: settings section name
        :param configuration: configuration instance
        """
        self.link_path = configuration.get(section, "link_path")

        # base template vars
        self.homepage = configuration.get(section, "homepage", fallback=None)
        self.name = configuration.get("repository", "name")

        self.sign_targets, self.default_pgp_key = GPG.sign_options(configuration)

    def make_html(self, result: Result, template_path: Path) -> str:
        """
        generate report for the specified packages
        :param result: build result
        :param template_path: path to jinja template
        """
        # idea comes from https://stackoverflow.com/a/38642558
        loader = jinja2.FileSystemLoader(searchpath=template_path.parent)
        environment = jinja2.Environment(loader=loader, autoescape=True)
        template = environment.get_template(template_path.name)

        content = [
            {
                "architecture": properties.architecture or "",
                "archive_size": pretty_size(properties.archive_size),
                "build_date": pretty_datetime(properties.build_date),
                "depends": properties.depends,
                "description": properties.description or "",
                "filename": properties.filename,
                "groups": properties.groups,
                "installed_size": pretty_size(properties.installed_size),
                "licenses": properties.licenses,
                "name": package,
                "url": properties.url or "",
                "version": base.version
            } for base in result.updated for package, properties in base.packages.items()
        ]
        comparator: Callable[[Dict[str, str]], str] = lambda item: item["filename"]

        return template.render(
            homepage=self.homepage,
            link_path=self.link_path,
            has_package_signed=SignSettings.Packages in self.sign_targets,
            has_repo_signed=SignSettings.Repository in self.sign_targets,
            packages=sorted(content, key=comparator),
            pgp_key=self.default_pgp_key,
            repository=self.name)
