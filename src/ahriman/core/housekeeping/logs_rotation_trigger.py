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
from ahriman.core import context
from ahriman.core.configuration import Configuration
from ahriman.core.status import Client
from ahriman.core.triggers import Trigger
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId
from ahriman.models.result import Result


class LogsRotationTrigger(Trigger):
    """
    rotate logs after build processes

    Attributes:
        keep_last_records(int): number of last records to keep
    """

    CONFIGURATION_SCHEMA = {
        "logs-rotation": {
            "type": "dict",
            "schema": {
                "keep_last_logs": {
                    "type": "integer",
                    "required": True,
                    "coerce": "integer",
                    "min": 0,
                },
            },
        },
    }
    REQUIRES_REPOSITORY = True

    def __init__(self, repository_id: RepositoryId, configuration: Configuration) -> None:
        """
        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
        """
        Trigger.__init__(self, repository_id, configuration)

        section = next(iter(self.configuration_sections(configuration)))
        self.keep_last_records = configuration.getint(  # read old-style first and then fallback to new style
            "settings", "keep_last_logs",
            fallback=configuration.getint(section, "keep_last_logs"))

    @classmethod
    def configuration_sections(cls, configuration: Configuration) -> list[str]:
        """
        extract configuration sections from configuration

        Args:
            configuration(Configuration): configuration instance

        Returns:
            list[str]: read configuration sections belong to this trigger
        """
        return list(cls.CONFIGURATION_SCHEMA.keys())

    def on_result(self, result: Result, packages: list[Package]) -> None:
        """
        run trigger

        Args:
            result(Result): build result
            packages(list[Package]): list of all available packages
        """
        ctx = context.get()
        reporter = ctx.get(Client)
        reporter.logs_rotate(self.keep_last_records)
