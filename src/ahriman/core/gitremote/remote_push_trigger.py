#
# Copyright (c) 2021-2024 ahriman team.
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
from ahriman.core.database import SQLite
from ahriman.core.gitremote.remote_push import RemotePush
from ahriman.core.triggers import Trigger
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId
from ahriman.models.result import Result


class RemotePushTrigger(Trigger):
    """
    trigger for syncing PKGBUILDs to remote repository

    Attributes:
        targets(list[str]): git remote target list
    """

    CONFIGURATION_SCHEMA = {
        "remote-push": {
            "type": "dict",
            "schema": {
                "target": {
                    "type": "list",
                    "coerce": "list",
                    "schema": {
                        "type": "string",
                        "empty": False,
                    },
                },
            },
        },
        "gitremote": {
            "type": "dict",
            "schema": {
                "commit_email": {
                    "type": "string",
                    "empty": False,
                },
                "commit_user": {
                    "type": "string",
                    "empty": False,
                },
                "push_url": {
                    "type": "string",
                    "required": True,
                    "empty": False,
                },
                "push_branch": {
                    "type": "string",
                    "empty": False,
                },
            },
        },
    }
    CONFIGURATION_SCHEMA_FALLBACK = "gitremote"

    def __init__(self, repository_id: RepositoryId, configuration: Configuration) -> None:
        """
        default constructor

        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
        """
        Trigger.__init__(self, repository_id, configuration)
        self.targets = self.configuration_sections(configuration)

    @classmethod
    def configuration_sections(cls, configuration: Configuration) -> list[str]:
        """
        extract configuration sections from configuration

        Args:
            configuration(Configuration): configuration instance

        Returns:
            list[str]: read configuration sections belong to this trigger
        """
        return configuration.getlist("remote-push", "target", fallback=[])

    def on_result(self, result: Result, packages: list[Package]) -> None:
        """
        trigger action which will be called after build process with process result

        Args:
            result(Result): build result
            packages(list[Package]): list of all available packages

        Raises:
            GitRemoteError: if database is not set in context
        """
        ctx = context.get()
        database = ctx.get(SQLite)

        for target in self.targets:
            section, _ = self.configuration.gettype(
                target, self.repository_id, fallback=self.CONFIGURATION_SCHEMA_FALLBACK)
            runner = RemotePush(database, self.configuration, section)
            runner.run(result)
