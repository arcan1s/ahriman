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
import argparse
import copy

from typing import Any, Callable, Dict, Optional, Type

from ahriman.application.handlers import Handler
from ahriman.core.configuration import Configuration
from ahriman.core.configuration.schema import CONFIGURATION_SCHEMA, \
    GITREMOTE_REMOTE_PULL_SCHEMA, GITREMOTE_REMOTE_PUSH_SCHEMA, \
    REPORT_CONSOLE_SCHEMA, REPORT_EMAIL_SCHEMA, REPORT_HTML_SCHEMA, REPORT_TELEGRAM_SCHEMA,\
    UPLOAD_GITHUB_SCHEMA, UPLOAD_RSYNC_SCHEMA, UPLOAD_S3_SCHEMA
from ahriman.core.configuration.validator import Validator
from ahriman.core.formatters import ValidationPrinter


class Validate(Handler):
    """
    configuration validator handler
    """

    ALLOW_AUTO_ARCHITECTURE_RUN = False

    @classmethod
    def run(cls: Type[Handler], args: argparse.Namespace, architecture: str, configuration: Configuration, *,
            report: bool, unsafe: bool) -> None:
        """
        callback for command line

        Args:
            args(argparse.Namespace): command line args
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting
            unsafe(bool): if set no user check will be performed before path creation
        """
        schema = Validate.schema(architecture, configuration)
        validator = Validator(instance=configuration, schema=schema)

        if validator.validate(configuration.dump()):
            return  # no errors found
        for node, errors in validator.errors.items():
            ValidationPrinter(node, errors).print(verbose=True)

        # as we reach this part it means that we always have errors
        Validate.check_if_empty(args.exit_code, True)

    @staticmethod
    def schema(architecture: str, configuration: Configuration) -> Dict[str, Any]:
        """
        get schema with triggers

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance

        Returns:
            Dict[str, Any]: configuration validation schema
        """
        root = copy.deepcopy(CONFIGURATION_SCHEMA)

        # that's actually bad design, but in order to validate built-in triggers we need to know which are set
        Validate.schema_insert(architecture, configuration, root, "remote-pull", lambda _: GITREMOTE_REMOTE_PULL_SCHEMA)
        Validate.schema_insert(architecture, configuration, root, "remote-push", lambda _: GITREMOTE_REMOTE_PUSH_SCHEMA)

        report_schemas = {
            "console": REPORT_CONSOLE_SCHEMA,
            "email": REPORT_EMAIL_SCHEMA,
            "html": REPORT_HTML_SCHEMA,
            "telegram": REPORT_TELEGRAM_SCHEMA,
        }
        for schema_name, schema in report_schemas.items():
            root[schema_name] = Validate.schema_erase_required(copy.deepcopy(schema))
        Validate.schema_insert(architecture, configuration, root, "report", report_schemas.get)

        upload_schemas = {
            "github": UPLOAD_GITHUB_SCHEMA,
            "rsync": UPLOAD_RSYNC_SCHEMA,
            "s3": UPLOAD_S3_SCHEMA,
        }
        for schema_name, schema in upload_schemas.items():
            root[schema_name] = Validate.schema_erase_required(copy.deepcopy(schema))
        Validate.schema_insert(architecture, configuration, root, "upload", upload_schemas.get)

        return root

    @staticmethod
    def schema_erase_required(schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        recursively remove required field from supplied cerberus schema

        Args:
            schema(Dict[str, Any]): source schema from which required field must be removed

        Returns:
            Dict[str, Any]: schema without required fields
        """
        schema.pop("required", None)
        for value in filter(lambda v: isinstance(v, dict), schema.values()):
            Validate.schema_erase_required(value)
        return schema

    @staticmethod
    def schema_insert(architecture: str, configuration: Configuration, root: Dict[str, Any], root_section: str,
                      schema_mapping: Callable[[str], Optional[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        insert child schema into the root schema based on mapping rules

        Notes:
            Actually it is a bad design, because we are reading triggers configuration from parsers which (basically)
        don't know anything about triggers. But in order to validate built-in triggers we need to know which are set

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            root(Dict[str, Any]): root schema in which child schema will be inserted
            root_section(str): section name in root schema
            schema_mapping(Callable[[str], Optional[Dict[str, Any]]]): extractor for child schema based on trigger type

        Returns:
            Dict[str, Any]: modified root schema. Note, however, that schema will be modified in place
        """
        if not configuration.has_section(root_section):
            return root

        targets = configuration.getlist(root_section, "target", fallback=[])
        for target in targets:
            section, schema_name = configuration.gettype(target, architecture)
            if (schema := schema_mapping(schema_name)) is not None:
                root[section] = copy.deepcopy(schema)

        return root
