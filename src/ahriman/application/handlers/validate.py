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
import argparse
import copy

from typing import Any

from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.core.configuration.schema import CONFIGURATION_SCHEMA, ConfigurationSchema
from ahriman.core.exceptions import ExtensionError
from ahriman.core.formatters import ValidationPrinter
from ahriman.core.triggers import TriggerLoader
from ahriman.models.repository_id import RepositoryId


class Validate(Handler):
    """
    configuration validator handler
    """

    ALLOW_MULTI_ARCHITECTURE_RUN = False  # conflicting io

    @classmethod
    def run(cls, args: argparse.Namespace, repository_id: RepositoryId, configuration: Configuration, *,
            report: bool) -> None:
        """
        callback for command line

        Args:
            args(argparse.Namespace): command line args
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting
        """
        from ahriman.core.configuration.validator import Validator

        schema = Validate.schema(configuration)
        validator = Validator(configuration=configuration, schema=schema)

        if validator.validate(configuration.dump()):
            return  # no errors found
        for node, errors in validator.errors.items():
            ValidationPrinter(node, errors)(verbose=True)

        # as we reach this part it means that we always have errors
        Validate.check_status(args.exit_code, False)

    @staticmethod
    def _set_service_config_validate_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for config validation subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("service-config-validate", aliases=["config-validate", "repo-config-validate"],
                                 help="validate system configuration",
                                 description="validate configuration and print found errors")
        parser.add_argument("-e", "--exit-code", help="return non-zero exit status if configuration is invalid",
                            action="store_true")
        parser.set_defaults(lock=None, quiet=True, report=False, unsafe=True)
        return parser

    @staticmethod
    def schema(configuration: Configuration) -> ConfigurationSchema:
        """
        get schema with triggers

        Args:
            configuration(Configuration): configuration instance

        Returns:
            ConfigurationSchema: configuration validation schema
        """
        root = copy.deepcopy(CONFIGURATION_SCHEMA)

        # create trigger loader instance
        loader = TriggerLoader()
        triggers = loader.selected_triggers(configuration) + loader.known_triggers(configuration)

        for trigger in set(triggers):
            try:
                trigger_class = loader.load_trigger_class(trigger)
            except ExtensionError:
                continue

            # default settings if any
            for schema_name, schema in trigger_class.configuration_schema(None).items():
                erased = Validate.schema_erase_required(copy.deepcopy(schema))
                root[schema_name] = Validate.schema_merge(root.get(schema_name, {}), erased)

            # settings according to enabled triggers
            for schema_name, schema in trigger_class.configuration_schema(configuration).items():
                root[schema_name] = Validate.schema_merge(root.get(schema_name, {}), copy.deepcopy(schema))

        return root

    @staticmethod
    def schema_erase_required(schema: ConfigurationSchema) -> ConfigurationSchema:
        """
        recursively remove required field from supplied cerberus schema

        Args:
            schema(ConfigurationSchema): source schema from which required field must be removed

        Returns:
            ConfigurationSchema: schema without required fields. Note, that source schema will be modified in-place
        """
        schema.pop("required", None)
        for value in filter(lambda v: isinstance(v, dict), schema.values()):
            Validate.schema_erase_required(value)
        return schema

    @staticmethod
    def schema_merge(source: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
        """
        merge child schema into source. In case if source already contains values, new keys will be added
            (possibly with overrides - in case if such key already set also)

        Args:
            source(dict[str, Any]): source (current) schema into which will be merged
            schema(dict[str, Any]): new schema to be merged

        Returns:
            dict[str, Any]: schema with added elements from source schema if they were set before and not presented
            in the new one. Note, that schema will be modified in-place
        """
        for key, value in source.items():
            if key not in schema:
                schema[key] = value  # new key found, just add it as is
            elif isinstance(value, dict):
                # value is dictionary, so we need to go deeper
                Validate.schema_merge(value, schema[key])

        return schema

    arguments = [_set_service_config_validate_parser]
