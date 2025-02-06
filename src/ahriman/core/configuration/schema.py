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
                "path_exists": True,
                "path_type": "dir",
            },
            "keep_last_logs": {
                "type": "integer",
                "coerce": "integer",
                "min": 0,
            },
            "logging": {
                "type": "path",
                "coerce": "absolute_path",
                "required": True,
                "path_exists": True,
                "path_type": "file",
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
                "empty": False,
                "is_url": [],
            },
            "repositories": {
                "type": "list",
                "coerce": "list",
                "schema": {
                    "type": "string",
                    "empty": False,
                },
                "required": True,
                "empty": False,
            },
            "root": {
                "type": "path",
                "coerce": "absolute_path",
                "required": True,
                "path_exists": True,
                "path_type": "dir",
            },
            "sync_files_database": {
                "type": "boolean",
                "coerce": "boolean",
                "required": True,
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
                    {"allowed": ["pam"], "dependencies": ["full_access_group"]},
                ],
            },
            "allow_read_only": {
                "type": "boolean",
                "coerce": "boolean",
                "required": True,
            },
            "client_id": {
                "type": "string",
                "empty": False,
            },
            "client_secret": {
                "type": "string",
                "empty": False,
            },
            "cookie_secret_key": {
                "type": "string",
                "minlength": 32,
                "maxlength": 64,  # we cannot verify maxlength, because base64 representation might be longer than bytes
            },
            "full_access_group": {
                "type": "string",
                "empty": False,
            },
            "max_age": {
                "type": "integer",
                "coerce": "integer",
                "min": 0,
            },
            "oauth_icon": {
                "type": "string",
                "empty": False,
            },
            "oauth_provider": {
                "type": "string",
                "empty": False,
            },
            "oauth_scopes": {
                "type": "string",
                "empty": False,
            },
            "permit_root_login": {
                "type": "boolean",
                "coerce": "boolean",
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
                "schema": {
                    "type": "string",
                    "empty": False,
                },
            },
            "build_command": {
                "type": "string",
                "required": True,
                "empty": False,
            },
            "ignore_packages": {
                "type": "list",
                "coerce": "list",
                "schema": {
                    "type": "string",
                    "empty": False,
                },
            },
            "include_debug_packages": {
                "type": "boolean",
                "coerce": "boolean",
            },
            "makepkg_flags": {
                "type": "list",
                "coerce": "list",
                "schema": {
                    "type": "string",
                    "empty": False,
                },
            },
            "makechrootpkg_flags": {
                "type": "list",
                "coerce": "list",
                "schema": {
                    "type": "string",
                    "empty": False,
                },
            },
            "scan_paths": {
                "type": "list",
                "coerce": "list",
                "schema": {
                    "type": "string",
                    "empty": False,
                },
            },
            "triggers": {
                "type": "list",
                "coerce": "list",
                "schema": {
                    "type": "string",
                    "empty": False,
                },
            },
            "triggers_known": {
                "type": "list",
                "coerce": "list",
                "schema": {
                    "type": "string",
                    "empty": False,
                },
            },
            "vcs_allowed_age": {
                "type": "integer",
                "coerce": "integer",
                "min": 0,
            },
            "workers": {
                "type": "list",
                "coerce": "list",
                "schema": {
                    "type": "string",
                    "empty": False,
                    "is_url": [],
                },
            },
        },
    },
    "repository": {
        "type": "dict",
        "schema": {
            "name": {
                "type": "string",
                "empty": False,
            },
            "root": {
                "type": "path",
                "coerce": "absolute_path",
                "required": True,
                "path_exists": True,
                "path_type": "dir",
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
                "empty": False,
            },
        },
    },
    "status": {
        "type": "dict",
        "schema": {
            "enabled": {
                "type": "boolean",
                "coerce": "boolean",
            },
            "address": {
                "type": "string",
                "empty": False,
                "is_url": [],
            },
            "password": {
                "type": "string",
                "empty": False,
            },
            "suppress_http_log_errors": {
                "type": "boolean",
                "coerce": "boolean",
            },
            "timeout": {
                "type": "integer",
                "coerce": "integer",
                "min": 0,
            },
            "username": {
                "type": "string",
                "empty": False,
            },
        },
    },
    "web": {
        "type": "dict",
        "schema": {
            "address": {
                "type": "string",
                "empty": False,
                "is_url": ["http", "https"],
            },
            "enable_archive_upload": {
                "type": "boolean",
                "coerce": "boolean",
            },
            "host": {
                "type": "string",
                "empty": False,
                "is_ip_address": ["localhost"],
            },
            "index_url": {
                "type": "string",
                "empty": False,
                "is_url": ["http", "https"],
            },
            "max_body_size": {
                "type": "integer",
                "coerce": "integer",
                "min": 0,
            },
            "password": {
                "type": "string",
                "empty": False,
            },
            "port": {
                "type": "integer",
                "coerce": "integer",
                "min": 0,
                "max": 65535,
            },
            "service_only": {
                "type": "boolean",
                "coerce": "boolean",
            },
            "static_path": {
                "type": "path",
                "coerce": "absolute_path",
                "required": True,
                "path_exists": True,
                "path_type": "dir",
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
                "empty": False,
            },
            "wait_timeout": {
                "type": "integer",
                "coerce": "integer",
            }
        },
    },
}
