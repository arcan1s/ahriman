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
from ahriman.core.report.report import Report
from ahriman.core.triggers import Trigger
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId
from ahriman.models.result import Result


class ReportTrigger(Trigger):
    """
    report trigger

    Attributes:
        targets(list[str]): report target list
    """

    CONFIGURATION_SCHEMA = {
        "report": {
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
        "console": {
            "type": "dict",
            "schema": {
                "type": {
                    "type": "string",
                    "allowed": ["console"],
                },
                "use_utf": {
                    "type": "boolean",
                    "coerce": "boolean",
                },
            },
        },
        "email": {
            "type": "dict",
            "schema": {
                "type": {
                    "type": "string",
                    "allowed": ["email"],
                },
                "homepage": {
                    "type": "string",
                    "empty": False,
                    "is_url": ["http", "https"],
                },
                "host": {
                    "type": "string",
                    "required": True,
                    "empty": False,
                },
                "link_path": {
                    "type": "string",
                    "required": True,
                    "empty": False,
                    "is_url": [],
                },
                "no_empty_report": {
                    "type": "boolean",
                    "coerce": "boolean",
                },
                "password": {
                    "type": "string",
                    "empty": False,
                },
                "port": {
                    "type": "integer",
                    "coerce": "integer",
                    "required": True,
                    "min": 0,
                    "max": 65535,
                },
                "receivers": {
                    "type": "list",
                    "coerce": "list",
                    "schema": {
                        "type": "string",
                        "empty": False,
                    },
                    "required": True,
                    "empty": False,
                },
                "rss_url": {
                    "type": "string",
                    "empty": False,
                    "is_url": ["http", "https"],
                },
                "sender": {
                    "type": "string",
                    "required": True,
                    "empty": False,
                },
                "ssl": {
                    "type": "string",
                    "allowed": ["ssl", "starttls", "disabled"],
                },
                "template": {
                    "type": "string",
                    "dependencies": ["templates"],
                    "required": True,
                    "empty": False,
                },
                "template_full": {
                    "type": "string",
                    "dependencies": ["templates"],
                    "required": True,
                    "empty": False,
                },
                "templates": {
                    "type": "list",
                    "coerce": "list",
                    "schema": {
                        "type": "path",
                        "coerce": "absolute_path",
                        "path_exists": True,
                        "path_type": "dir",
                    },
                    "empty": False,
                },
                "user": {
                    "type": "string",
                    "empty": False,
                },
            },
        },
        "html": {
            "type": "dict",
            "schema": {
                "type": {
                    "type": "string",
                    "allowed": ["html"],
                },
                "homepage": {
                    "type": "string",
                    "empty": False,
                    "is_url": ["http", "https"],
                },
                "link_path": {
                    "type": "string",
                    "required": True,
                    "empty": False,
                    "is_url": [],
                },
                "path": {
                    "type": "path",
                    "coerce": "absolute_path",
                    "required": True,
                },
                "rss_url": {
                    "type": "string",
                    "empty": False,
                    "is_url": ["http", "https"],
                },
                "template": {
                    "type": "string",
                    "dependencies": ["templates"],
                    "required": True,
                    "empty": False,
                },
                "templates": {
                    "type": "list",
                    "coerce": "list",
                    "schema": {
                        "type": "path",
                        "coerce": "absolute_path",
                        "path_exists": True,
                        "path_type": "dir",
                    },
                    "empty": False,
                },
            },
        },
        "remote-call": {
            "type": "dict",
            "schema": {
                "type": {
                    "type": "string",
                    "allowed": ["ahriman", "remote-call"],
                },
                "aur": {
                    "type": "boolean",
                    "coerce": "boolean",
                },
                "local": {
                    "type": "boolean",
                    "coerce": "boolean",
                },
                "manual": {
                    "type": "boolean",
                    "coerce": "boolean",
                },
                "wait_timeout": {
                    "type": "integer",
                    "coerce": "integer",
                },
            },
        },
        "rss": {
            "type": "dict",
            "schema": {
                "type": {
                    "type": "string",
                    "allowed": ["rss"],
                },
                "homepage": {
                    "type": "string",
                    "empty": False,
                    "is_url": ["http", "https"],
                },
                "link_path": {
                    "type": "string",
                    "required": True,
                    "empty": False,
                    "is_url": [],
                },
                "max_entries": {
                    "type": "integer",
                    "coerce": "integer",
                },
                "path": {
                    "type": "path",
                    "coerce": "absolute_path",
                    "required": True,
                },
                "rss_url": {
                    "type": "string",
                    "empty": False,
                    "is_url": ["http", "https"],
                },
                "template": {
                    "type": "string",
                    "dependencies": ["templates"],
                    "required": True,
                    "empty": False,
                },
                "templates": {
                    "type": "list",
                    "coerce": "list",
                    "schema": {
                        "type": "path",
                        "coerce": "absolute_path",
                        "path_exists": True,
                        "path_type": "dir",
                    },
                    "empty": False,
                },
            },
        },
        "telegram": {
            "type": "dict",
            "schema": {
                "type": {
                    "type": "string",
                    "allowed": ["telegram"],
                },
                "api_key": {
                    "type": "string",
                    "required": True,
                    "empty": False,
                },
                "chat_id": {
                    "type": "string",
                    "required": True,
                    "empty": False,
                },
                "homepage": {
                    "type": "string",
                    "empty": False,
                    "is_url": ["http", "https"],
                },
                "link_path": {
                    "type": "string",
                    "required": True,
                    "empty": False,
                    "is_url": [],
                },
                "rss_url": {
                    "type": "string",
                    "empty": False,
                    "is_url": ["http", "https"],
                },
                "template": {
                    "type": "string",
                    "dependencies": ["templates"],
                    "required": True,
                    "empty": False,
                },
                "template_type": {
                    "type": "string",
                    "allowed": ["MarkdownV2", "HTML", "Markdown"],
                },
                "templates": {
                    "type": "list",
                    "coerce": "list",
                    "schema": {
                        "type": "path",
                        "coerce": "absolute_path",
                        "path_exists": True,
                        "path_type": "dir",
                    },
                    "empty": False,
                },
                "timeout": {
                    "type": "integer",
                    "coerce": "integer",
                    "min": 0,
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
        return configuration.getlist("report", "target", fallback=[])

    def on_result(self, result: Result, packages: list[Package]) -> None:
        """
        run trigger

        Args:
            result(Result): build result
            packages(list[Package]): list of all available packages
        """
        for target in self.targets:
            runner = Report.load(self.repository_id, self.configuration, target)
            runner.run(result, packages)
