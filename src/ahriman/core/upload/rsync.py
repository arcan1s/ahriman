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
from ahriman.core.configuration import Configuration
from ahriman.core.upload.uploader import Uploader
from ahriman.core.util import check_output


class Rsync(Uploader):

    def __init__(self, architecture: str, config: Configuration) -> None:
        Uploader.__init__(self, architecture, config)
        section = self.config.get_section_name('rsync', self.architecture)
        self.remote = self.config.get(section, 'remote')

    def sync(self, path: str) -> None:
        check_output('rsync', '--archive', '--verbose', '--compress', '--partial', '--progress', '--delete', path, self.remote,
                     exception=None,
                     logger=self.logger)
