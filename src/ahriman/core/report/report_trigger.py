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
from ahriman.core.report.report import Report
from ahriman.models.package import Package
from ahriman.models.result import Result


class ReportTrigger(Trigger):
    """
    report trigger

    Attributes:
        targets(List[str]): report target list
    """

    CONFIGURATION_SCHEMA = {
        "report": {
            "type": "dict",
            "schema": {
                "target": {
                    "type": "list",
                    "coerce": "list",
                    "schema": {"type": "string"},
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
                "full_template_path": {
                    "type": "path",
                    "coerce": "absolute_path",
                    "path_exists": True,
                },
                "homepage": {
                    "type": "string",
                    "is_url": ["http", "https"],
                },
                "host": {
                    "type": "string",
                    "required": True,
                },
                "link_path": {
                    "type": "string",
                    "required": True,
                    "is_url": [],
                },
                "no_empty_report": {
                    "type": "boolean",
                    "coerce": "boolean",
                },
                "password": {
                    "type": "string",
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
                    "schema": {"type": "string"},
                    "required": True,
                    "empty": False,
                },
                "sender": {
                    "type": "string",
                    "required": True,
                },
                "ssl": {
                    "type": "string",
                    "allowed": ["ssl", "starttls", "disabled"],
                },
                "template_path": {
                    "type": "path",
                    "coerce": "absolute_path",
                    "required": True,
                    "path_exists": True,
                },
                "user": {
                    "type": "string",
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
                    "is_url": ["http", "https"],
                },
                "link_path": {
                    "type": "string",
                    "required": True,
                    "is_url": [],
                },
                "path": {
                    "type": "path",
                    "coerce": "absolute_path",
                    "required": True,
                },
                "template_path": {
                    "type": "path",
                    "coerce": "absolute_path",
                    "required": True,
                    "path_exists": True,
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
                },
                "chat_id": {
                    "type": "string",
                    "required": True,
                },
                "homepage": {
                    "type": "string",
                    "is_url": ["http", "https"],
                },
                "link_path": {
                    "type": "string",
                    "required": True,
                    "is_url": [],
                },
                "template_path": {
                    "type": "path",
                    "coerce": "absolute_path",
                    "required": True,
                    "path_exists": True,
                },
                "template_type": {
                    "type": "string",
                    "allowed": ["MarkdownV2", "HTML", "Markdown"],
                },
                "timeout": {
                    "type": "integer",
                    "coerce": "integer",
                    "min": 0,
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
        return configuration.getlist("report", "target", fallback=[])

    def on_result(self, result: Result, packages: Iterable[Package]) -> None:
        """
        run trigger

        Args:
            result(Result): build result
            packages(Iterable[Package]): list of all available packages
        """
        for target in self.targets:
            runner = Report.load(self.architecture, self.configuration, target)
            runner.run(result, packages)
