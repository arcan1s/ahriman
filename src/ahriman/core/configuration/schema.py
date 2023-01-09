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
# pylint: disable=too-many-lines
__all__ = [
    "CONFIGURATION_SCHEMA",
    "GITREMOTE_REMOTE_PULL_SCHEMA", "GITREMOTE_REMOTE_PUSH_SCHEMA",
    "REPORT_CONSOLE_SCHEMA", "REPORT_EMAIL_SCHEMA", "REPORT_HTML_SCHEMA", "REPORT_TELEGRAM_SCHEMA",
    "UPLOAD_GITHUB_SCHEMA", "UPLOAD_RSYNC_SCHEMA", "UPLOAD_S3_SCHEMA",
]


CONFIGURATION_SCHEMA = {
    "settings": {
        "type": "dict",
        "schema": {
            "include": {
                "type": "path",
                "coerce": "absolute_path",
                "required": True,
                "path_exists": True,
            },
            "database": {
                "type": "path",
                "coerce": "absolute_path",
                "required": True,
            },
            "logging": {
                "type": "path",
                "coerce": "absolute_path",
                "required": True,
                "path_exists": True,
            },
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
                    {"allowed": ["configuration", "mapping"], "dependencies": ["salt"]},
                    {"allowed": ["oauth"], "dependencies": [
                        "client_id", "client_secret", "oauth_provider", "oauth_scopes", "salt"
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
            "max_age": {
                "type": "integer",
                "coerce": "integer",
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
            "vcs_allowed_age": {
                "type": "integer",
                "coerce": "integer",
            },
        },
    },
    "repository": {
        "type": "dict",
        "schema": {
            "name": {
                "type": "string",
                "required": True,
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
        "keysrules": {
            "type": "string",
            "anyof_regex": ["^target$", "^key$", "^key_.*"],
        },
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
            "host": {
                "type": "string",
            },
            "index_url": {
                "type": "string",
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
        },
    },
    "remote-pull": {
        "type": "dict",
        "schema": {
            "target": {
                "type": "list",
                "coerce": "list",
                "schema": {"type": "string"},
            },
        },
    },
    "remote-push": {
        "type": "dict",
        "schema": {
            "target": {
                "type": "list",
                "coerce": "list",
                "schema": {"type": "string"},
            },
        },
    },
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
}


GITREMOTE_REMOTE_PULL_SCHEMA = {
    "type": "dict",
    "schema": {
        "pull_url": {
            "type": "string",
            "required": True,
        },
        "pull_branch": {
            "type": "string",
        },
    },
}


GITREMOTE_REMOTE_PUSH_SCHEMA = {
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
}


REPORT_CONSOLE_SCHEMA = {
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
}


REPORT_EMAIL_SCHEMA = {
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
        },
        "host": {
            "type": "string",
            "required": True,
        },
        "link_path": {
            "type": "string",
            "required": True,
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
}


REPORT_HTML_SCHEMA = {
    "type": "dict",
    "schema": {
        "type": {
            "type": "string",
            "allowed": ["html"],
        },
        "homepage": {
            "type": "string",
        },
        "link_path": {
            "type": "string",
            "required": True,
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
}


REPORT_TELEGRAM_SCHEMA = {
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
        },
        "link_path": {
            "type": "string",
            "required": True,
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
        },
    },
}


UPLOAD_GITHUB_SCHEMA = {
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
        },
        "username": {
            "type": "string",
        },
    },
}

UPLOAD_RSYNC_SCHEMA = {
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
}


UPLOAD_S3_SCHEMA = {
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
}
