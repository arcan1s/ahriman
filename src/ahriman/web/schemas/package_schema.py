#
# Copyright (c) 2021-2024 ahriman team.
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
from ahriman import __version__
from ahriman.web.apispec import Schema, fields
from ahriman.web.schemas.package_properties_schema import PackagePropertiesSchema
from ahriman.web.schemas.remote_schema import RemoteSchema


class PackageSchema(Schema):
    """
    request and response package schema
    """

    base = fields.String(required=True, metadata={
        "description": "Package base",
        "example": "ahriman",
    })
    version = fields.String(required=True, metadata={
        "description": "Package version",
        "example": __version__,
    })
    remote = fields.Nested(RemoteSchema(), required=True, metadata={
        "description": "Package remote properties",
    })
    packages = fields.Dict(
        keys=fields.String(), values=fields.Nested(PackagePropertiesSchema()), required=True, metadata={
            "description": "Packages which belong to this base",
        })
    packager = fields.String(metadata={
        "description": "packager for the last success package build",
        "example": "ahriman bot <ahriman@example.com>",
    })
