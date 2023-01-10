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
from typing import Iterable, List, Type

from ahriman.core import context
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.gitremote.remote_push import RemotePush
from ahriman.core.triggers import Trigger
from ahriman.models.context_key import ContextKey
from ahriman.models.package import Package
from ahriman.models.result import Result


class RemotePushTrigger(Trigger):
    """
    trigger for syncing PKGBUILDs to remote repository

    Attributes:
        targets(List[str]): git remote target list
    """

    CONFIGURATION_SCHEMA = {
        "gitremote": {
            "type": "dict",
            "schema": {
                "commit_author": {
                    "type": "string",
                },
                "push_url": {
                    "type": "string",
                    "required": True,
                },
                "push_branch": {
                    "type": "string",
                },
            },
        },
    }
    CONFIGURATION_SCHEMA_FALLBACK = "gitremote"

    def __init__(self, architecture: str, configuration: Configuration) -> None:
        """
        default constructor

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
        """
        Trigger.__init__(self, architecture, configuration)
        self.targets = self.configuration_sections(configuration)

    @classmethod
    def configuration_sections(cls: Type[Trigger], configuration: Configuration) -> List[str]:
        """
        extract configuration sections from configuration

        Args:
            configuration(Configuration): configuration instance

        Returns:
            List[str]: read configuration sections belong to this trigger
        """
        return configuration.getlist("remote-push", "target", fallback=[])

    def on_result(self, result: Result, packages: Iterable[Package]) -> None:
        """
        trigger action which will be called after build process with process result

        Args:
            result(Result): build result
            packages(Iterable[Package]): list of all available packages

        Raises:
            GitRemoteError: if database is not set in context
        """
        ctx = context.get()
        database = ctx.get(ContextKey("database", SQLite))

        for target in self.targets:
            section, _ = self.configuration.gettype(
                target, self.architecture, fallback=self.CONFIGURATION_SCHEMA_FALLBACK)
            runner = RemotePush(self.configuration, database, section)
            runner.run(result)
