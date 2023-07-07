#
# Copyright (c) 2021-2023 ahriman team.
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
from ahriman.core.database import SQLite
from ahriman.core.log import LazyLogging
from ahriman.core.repository import Repository
from ahriman.models.pacman_synchronization import PacmanSynchronization


class ApplicationProperties(LazyLogging):
    """
    application base properties class

    Attributes:
        architecture(str): repository architecture
        configuration(Configuration): configuration instance
        database(SQLite): database instance
        repository(Repository): repository instance
    """

    def __init__(self, architecture: str, configuration: Configuration, *, report: bool,
                 refresh_pacman_database: PacmanSynchronization = PacmanSynchronization.Disabled) -> None:
        """
        default constructor

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting
            refresh_pacman_database(PacmanSynchronization, optional): pacman database synchronization level
                (Default value = PacmanSynchronization.Disabled)
        """
        self.configuration = configuration
        self.architecture = architecture
        self.database = SQLite.load(configuration)
        self.repository = Repository.load(architecture, configuration, self.database, report=report,
                                          refresh_pacman_database=refresh_pacman_database)
