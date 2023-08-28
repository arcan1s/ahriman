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
from typing import Any


__all__ = ["CONFIGURATION_SCHEMA", "ConfigurationSchema"]


ConfigurationSchema = dict[str, dict[str, Any]]


CONFIGURATION_SCHEMA: ConfigurationSchema = {
    "settings": {
        "type": "dict",
        "schema": {
            "apply_migrations": {
                "type": "boolean",
                "coerce": "boolean",
            },
            "database": {
                "type": "path",
                "coerce": "absolute_path",
                "required": True,
            },
            "include": {
                "type": "path",
                "coerce": "absolute_path",
                "required": True,
                "path_exists": True,
            },
            "logging": {
                "type": "path",
                "coerce": "absolute_path",
                "required": True,
                "path_exists": True,
            },
            "suppress_http_log_errors": {
                "type": "boolean",
                "coerce": "boolean",
            }
        },
    },
    "alpm": {
        "type": "dict",
        "schema": {
            "database": {
                "type": "path",
                "coerce": "absolute_path",
                "required": True,
            },
            "mirror": {
                "type": "string",
                "required": True,
                "is_url": [],
            },
            "repositories": {
                "type": "list",
                "coerce": "list",
                "schema": {"type": "string"},
                "required": True,
                "empty": False,
            },
            "root": {
                "type": "path",
                "coerce": "absolute_path",
                "required": True,
                "path_exists": True,
            },
            "use_ahriman_cache": {
                "type": "boolean",
                "coerce": "boolean",
                "required": True,
            },
        },
    },
    "auth": {
        "type": "dict",
        "schema": {
            "target": {
                "type": "string",
                "oneof": [
                    {"allowed": ["disabled"]},
                    {"allowed": ["configuration", "mapping"]},
                    {"allowed": ["oauth"], "dependencies": [
                        "client_id",
                        "client_secret",
                        "oauth_provider",
                        "oauth_scopes",
                    ]},
                ],
            },
            "allow_read_only": {
                "type": "boolean",
                "coerce": "boolean",
                "required": True,
            },
            "client_id": {
                "type": "string",
            },
            "client_secret": {
                "type": "string",
            },
            "cookie_secret_key": {
                "type": "string",
                "minlength": 32,
                "maxlength": 64,  # we cannot verify maxlength, because base64 representation might be longer than bytes
            },
            "max_age": {
                "type": "integer",
                "coerce": "integer",
                "min": 0,
            },
            "oauth_provider": {
                "type": "string",
            },
            "oauth_scopes": {
                "type": "string",
            },
            "salt": {
                "type": "string",
            },
        },
    },
    "build": {
        "type": "dict",
        "schema": {
            "archbuild_flags": {
                "type": "list",
                "coerce": "list",
                "schema": {"type": "string"},
            },
            "build_command": {
                "type": "string",
                "required": True,
            },
            "ignore_packages": {
                "type": "list",
                "coerce": "list",
                "schema": {"type": "string"},
            },
            "makepkg_flags": {
                "type": "list",
                "coerce": "list",
                "schema": {"type": "string"},
            },
            "makechrootpkg_flags": {
                "type": "list",
                "coerce": "list",
                "schema": {"type": "string"},
            },
            "triggers": {
                "type": "list",
                "coerce": "list",
                "schema": {"type": "string"},
            },
            "triggers_known": {
                "type": "list",
                "coerce": "list",
                "schema": {"type": "string"},
            },
            "vcs_allowed_age": {
                "type": "integer",
                "coerce": "integer",
                "min": 0,
            },
        },
    },
    "repository": {
        "type": "dict",
        "schema": {
            "name": {
                "type": "string",
            },
            "root": {
                "type": "string",
                "required": True,
            },
        },
    },
    "sign": {
        "type": "dict",
        "allow_unknown": True,
        "schema": {
            "target": {
                "type": "list",
                "coerce": "list",
                "oneof": [
                    {"allowed": []},
                    {"allowed": ["package", "repository"], "dependencies": ["key"]},
                ],
            },
            "key": {
                "type": "string",
            },
        },
    },
    "web": {
        "type": "dict",
        "schema": {
            "address": {
                "type": "string",
                "is_url": ["http", "https"],
            },
            "debug": {
                "type": "boolean",
                "coerce": "boolean",
            },
            "debug_check_host": {
                "type": "boolean",
                "coerce": "boolean",
            },
            "debug_allowed_hosts": {
                "type": "list",
                "coerce": "list",
                "schema": {"type": "string"},
            },
            "enable_archive_upload": {
                "type": "boolean",
                "coerce": "boolean",
            },
            "host": {
                "type": "string",
                "is_ip_address": ["localhost"],
            },
            "index_url": {
                "type": "string",
                "is_url": ["http", "https"],
            },
            "max_body_size": {
                "type": "integer",
                "coerce": "integer",
                "min": 0,
            },
            "password": {
                "type": "string",
            },
            "port": {
                "type": "integer",
                "coerce": "integer",
                "min": 0,
                "max": 65535,
            },
            "static_path": {
                "type": "path",
                "coerce": "absolute_path",
                "required": True,
                "path_exists": True,
            },
            "templates": {
                "type": "path",
                "coerce": "absolute_path",
                "required": True,
                "path_exists": True,
            },
            "timeout": {
                "type": "integer",
                "coerce": "integer",
                "min": 0,
            },
            "unix_socket": {
                "type": "path",
                "coerce": "absolute_path",
            },
            "unix_socket_unsafe": {
                "type": "boolean",
                "coerce": "boolean",
            },
            "username": {
                "type": "string",
            },
            "wait_timeout": {
                "type": "integer",
                "coerce": "integer",
            }
        },
    },
}
