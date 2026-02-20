#
# Copyright (c) 2021-2026 ahriman team.
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
from ahriman.core.triggers import Trigger
from ahriman.core.upload.upload import Upload
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId
from ahriman.models.result import Result


class UploadTrigger(Trigger):
    """
    synchronization trigger

    Attributes:
        targets(list[str]): upload target list
    """

    CONFIGURATION_SCHEMA = {
        "upload": {
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
        "github": {
            "type": "dict",
            "schema": {
                "type": {
                    "type": "string",
                    "allowed": ["github"],
                },
                "max_retries": {
                    "type": "integer",
                    "coerce": "integer",
                    "min": 0,
                },
                "owner": {
                    "type": "string",
                    "required": True,
                    "empty": False,
                },
                "password": {
                    "type": "string",
                    "empty": False,
                },
                "repository": {
                    "type": "string",
                    "required": True,
                    "empty": False,
                },
                "retry_backoff": {
                    "type": "float",
                    "coerce": "float",
                    "min": 0,
                },
                "timeout": {
                    "type": "integer",
                    "coerce": "integer",
                    "min": 0,
                },
                "use_full_release_name": {
                    "type": "boolean",
                    "coerce": "boolean",
                },
                "username": {
                    "type": "string",
                    "empty": False,
                },
            },
        },
        "remote-service": {
            "type": "dict",
            "schema": {
                "type": {
                    "type": "string",
                    "allowed": ["ahriman", "remote-service"],
                },
                "max_retries": {
                    "type": "integer",
                    "coerce": "integer",
                    "min": 0,
                },
                "retry_backoff": {
                    "type": "float",
                    "coerce": "float",
                    "min": 0,
                },
                "timeout": {
                    "type": "integer",
                    "coerce": "integer",
                    "min": 0,
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
                    "schema": {
                        "type": "string",
                        "empty": False,
                    },
                    "required": True,
                    "empty": False,
                },
                "remote": {
                    "type": "string",
                    "required": True,
                    "empty": False,
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
                    "empty": False,
                },
                "bucket": {
                    "type": "string",
                    "required": True,
                    "empty": False,
                },
                "chunk_size": {
                    "type": "integer",
                    "coerce": "integer",
                    "min": 0,
                },
                "object_path": {
                    "type": "string",
                    "empty": False,
                },
                "region": {
                    "type": "string",
                    "required": True,
                    "empty": False,
                },
                "secret_key": {
                    "type": "string",
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
        return configuration.getlist("upload", "target", fallback=[])

    def on_result(self, result: Result, packages: list[Package]) -> None:
        """
        run trigger

        Args:
            result(Result): build result
            packages(list[Package]): list of all available packages
        """
        for target in self.targets:
            runner = Upload.load(self.repository_id, self.configuration, target)
            runner.run(self.configuration.repository_paths.repository, result.success)
