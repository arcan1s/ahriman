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

from typing import Dict

from ahriman.core.configuration import Configuration
from ahriman.core.report.report import Report
from ahriman.core.util import package_like
from ahriman.models.sign_settings import SignSettings


class HTML(Report):

    def __init__(self, architecture: str, config: Configuration) -> None:
        Report.__init__(self, architecture, config)
        section = self.config.get_section_name('html', self.architecture)
        self.report_path = config.get(section, 'path')

        self.link_path = config.get(section, 'link_path')
        self.template_path = config.get(section, 'template_path')

        # base template vars
        if SignSettings.from_option(config.get('sign', 'enabled')) != SignSettings.Disabled:
            self.pgp_key = config.get('sign', 'key', fallback=None)
        else:
            self.pgp_key = None
        self.homepage = config.get(section, 'homepage', fallback=None)
        self.repository = config.get('repository', 'name')

    def generate(self, path: str) -> None:
        # idea comes from https://stackoverflow.com/a/38642558
        templates_dir, template_name = os.path.split(self.template_path)
        loader = jinja2.FileSystemLoader(searchpath=templates_dir)
        environment = jinja2.Environment(loader=loader)
        template = environment.get_template(template_name)

        packages: Dict[str, str] = {}
        for fn in sorted(os.listdir(path)):
            if not package_like(fn):
                continue
            packages[fn] = f'{self.link_path}/{fn}'

        html = template.render(
            homepage=self.homepage,
            link_path=self.link_path,
            packages=packages,
            pgp_key=self.pgp_key,
            repository=self.repository)

        with open(self.report_path, 'w') as out:
            out.write(html)
