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
import os

from ahriman.core.configuration import Configuration
from ahriman.core.report.report import Report


class HTML(Report):

    def __init__(self, config: Configuration) -> None:
        Report.__init__(self, config)
        self.report_path = config.get('html', 'path')
        self.css_path = config.get('html', 'css_path')
        self.link_path = config.get('html', 'link_path')
        self.title = config.get('repository', 'name')

    def generate(self, path: str) -> None:
        # lets not use libraries here
        html = f'''<html lang="en"><head><title>{self.title}</title>'''
        if self.css_path:
            html += f'''<link rel="stylesheet" type="text/css" href="{self.css_path}">'''
        html += '''</head><body>'''

        html += '''<ul>'''
        for package in sorted(os.listdir(path)):
            if '.pkg.' not in package:
                continue
            html += f'''<li><a href="{self.link_path}/{package}">{package}</a></li>'''
        html += '''</ul>'''

        html += '''</body></html>'''

        with open(self.report_path, 'w') as out:
            out.write(html)
