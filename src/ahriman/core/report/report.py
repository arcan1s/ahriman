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
import logging

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import ReportFailed
from ahriman.models.report_settings import ReportSettings


class Report:

    def __init__(self, architecture: str, config: Configuration) -> None:
        self.architecture = architecture
        self.config = config
        self.logger = logging.getLogger('builder')

    @staticmethod
    def run(architecture: str, config: Configuration, target: str, path: str) -> None:
        provider = ReportSettings.from_option(target)
        if provider == ReportSettings.HTML:
            from ahriman.core.report.html import HTML
            report: Report = HTML(architecture, config)
        else:
            from ahriman.core.report.dummy import Dummy
            report = Dummy(architecture, config)

        try:
            report.generate(path)
        except Exception as e:
            raise ReportFailed(e) from e

    def generate(self, path: str) -> None:
        raise NotImplementedError