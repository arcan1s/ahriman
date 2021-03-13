#
# Copyright (c) 2021 Evgenii Alekseev.
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
import os

from typing import Callable, Dict, Iterable

from ahriman.core.configuration import Configuration
from ahriman.core.report.report import Report
from ahriman.models.package import Package
from ahriman.models.sign_settings import SignSettings


class HTML(Report):

    def __init__(self, architecture: str, config: Configuration) -> None:
        Report.__init__(self, architecture, config)
        self.architecture = architecture
        section = config.get_section_name('html', architecture)
        self.report_path = config.get(section, 'path')
        self.link_path = config.get(section, 'link_path')
        self.template_path = config.get(section, 'template_path')

        # base template vars
        self.homepage = config.get(section, 'homepage', fallback=None)
        self.repository = config.get('repository', 'name')

        sign_section = config.get_section_name('sign', architecture)
        self.sign_targets = [SignSettings.from_option(opt) for opt in config.getlist(sign_section, 'target')]
        self.pgp_key = config.get(sign_section, 'key') if self.sign_targets else None

    def generate(self, packages: Iterable[Package]) -> None:
        # idea comes from https://stackoverflow.com/a/38642558
        templates_dir, template_name = os.path.split(self.template_path)
        loader = jinja2.FileSystemLoader(searchpath=templates_dir)
        environment = jinja2.Environment(loader=loader)
        template = environment.get_template(template_name)

        content = [
            {
                'filename': filename,
                'name': package,
                'version': base.version
            } for base in packages for package, filename in base.packages.items()
        ]
        comparator: Callable[[Dict[str, str]], str] = lambda item: item['filename']

        html = template.render(
            architecture=self.architecture,
            homepage=self.homepage,
            link_path=self.link_path,
            has_package_signed=SignSettings.SignPackages in self.sign_targets,
            has_repo_signed=SignSettings.SignRepository in self.sign_targets,
            packages=sorted(content, key=comparator),
            pgp_key=self.pgp_key,
            repository=self.repository)

        with open(self.report_path, 'w') as out:
            out.write(html)
