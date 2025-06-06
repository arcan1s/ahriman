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
from ahriman.core.configuration import Configuration
from ahriman.core.support.package_creator import PackageCreator
from ahriman.core.support.pkgbuild.mirrorlist_generator import MirrorlistGenerator
from ahriman.core.triggers import Trigger
from ahriman.models.repository_id import RepositoryId


class MirrorlistTrigger(Trigger):
    """
    mirrorlist generator trigger

    Attributes:
        targets(list[str]): git remote target list
    """

    CONFIGURATION_SCHEMA = {
        "mirrorlist": {
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
        "mirrorlist-generator": {
            "type": "dict",
            "schema": {
                "type": {
                    "type": "string",
                    "allowed": ["mirrorlist-generator"],
                },
                "description": {
                    "type": "string",
                    "empty": False,
                },
                "homepage": {
                    "type": "string",
                    "empty": False,
                },
                "license": {
                    "type": "list",
                    "coerce": "list",
                    "schema": {
                        "type": "string",
                        "empty": False,
                    },
                },
                "package": {
                    "type": "string",
                    "empty": False,
                },
                "path": {
                    "type": "path",
                    "coerce": "absolute_path",
                },
                "servers": {
                    "type": "list",
                    "coerce": "list",
                    "schema": {
                        "type": "string",
                        "empty": False,
                    },
                    "required": True,
                    "empty": False,
                },
            },
        },
    }

    def __init__(self, repository_id: RepositoryId, configuration: Configuration) -> None:
        """
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
        return configuration.getlist("mirrorlist", "target", fallback=[])

    def on_start(self) -> None:
        """
        trigger action which will be called at the start of the application
        """
        for target in self.targets:
            generator = MirrorlistGenerator(self.repository_id, self.configuration, target)
            runner = PackageCreator(self.configuration, generator)
            runner.run()
