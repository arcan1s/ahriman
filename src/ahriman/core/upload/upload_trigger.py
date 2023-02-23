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

from ahriman.core.configuration import Configuration
from ahriman.core.triggers import Trigger
from ahriman.core.upload.upload import Upload
from ahriman.models.package import Package
from ahriman.models.result import Result


class UploadTrigger(Trigger):
    """
    synchronization trigger

    Attributes:
        targets(List[str]): upload target list
    """

    CONFIGURATION_SCHEMA = {
        "upload": {
            "type": "dict",
            "schema": {
                "target": {
                    "type": "list",
                    "coerce": "list",
                    "schema": {"type": "string"},
                },
            },
        },
        "github": {
            "type": "dict",
            "schema": {
                "type": {
                    "type": "string",
                    "allowed": ["github"],
                },
                "owner": {
                    "type": "string",
                    "required": True,
                },
                "password": {
                    "type": "string",
                    "required": True,
                },
                "repository": {
                    "type": "string",
                    "required": True,
                },
                "timeout": {
                    "type": "integer",
                    "coerce": "integer",
                    "min": 0,
                },
                "username": {
                    "type": "string",
                },
            },
        },
        "rsync": {
            "type": "dict",
            "schema": {
                "type": {
                    "type": "string",
                    "allowed": ["rsync"],
                },
                "command": {
                    "type": "list",
                    "coerce": "list",
                    "schema": {"type": "string"},
                    "required": True,
                    "empty": False,
                },
                "remote": {
                    "type": "string",
                    "required": True,
                },
            },
        },
        "s3": {
            "type": "dict",
            "schema": {
                "type": {
                    "type": "string",
                    "allowed": ["s3"],
                },
                "access_key": {
                    "type": "string",
                    "required": True,
                },
                "bucket": {
                    "type": "string",
                    "required": True,
                },
                "chunk_size": {
                    "type": "integer",
                    "coerce": "integer",
                    "min": 0,
                },
                "region": {
                    "type": "string",
                    "required": True,
                },
                "secret_key": {
                    "type": "string",
                    "required": True,
                },
            },
        },
    }

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
        return configuration.getlist("upload", "target", fallback=[])

    def on_result(self, result: Result, packages: Iterable[Package]) -> None:
        """
        run trigger

        Args:
            result(Result): build result
            packages(Iterable[Package]): list of all available packages
        """
        for target in self.targets:
            runner = Upload.load(self.architecture, self.configuration, target)
            runner.run(self.configuration.repository_paths.repository, result.success)
