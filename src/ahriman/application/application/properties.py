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
import logging

from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository


class Properties:
    """
    application base properties class
    :ivar architecture: repository architecture
    :ivar configuration: configuration instance
    :ivar logger: application logger
    :ivar repository: repository instance
    """

    def __init__(self, architecture: str, configuration: Configuration, no_report: bool, unsafe: bool) -> None:
        """
        default constructor
        :param architecture: repository architecture
        :param configuration: configuration instance
        :param no_report: force disable reporting
        :param unsafe: if set no user check will be performed before path creation
        """
        self.logger = logging.getLogger("root")
        self.configuration = configuration
        self.architecture = architecture
        self.repository = Repository(architecture, configuration, no_report, unsafe)
