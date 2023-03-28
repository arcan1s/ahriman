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
from marshmallow import Schema, fields


class PackagePropertiesSchema(Schema):
    """
    request and response package properties schema
    """

    architecture = fields.String(metadata={
        "description": "Package architecture",
        "example": "x86_64",
    })
    archive_size = fields.Integer(metadata={
        "description": "Archive size in bytes",
        "example": 287989,
    })
    build_date = fields.Integer(metadata={
        "description": "Package build timestamp",
        "example": 1680537091.233495,
    })
    depends = fields.List(fields.String(), metadata={
        "description": "Package dependencies list",
        "example": ["devtools"],
    })
    make_depends = fields.List(fields.String(), metadata={
        "description": "Package make dependencies list",
        "example": ["python-build"],
    })
    opt_depends = fields.List(fields.String(), metadata={
        "description": "Package optional dependencies list",
        "example": ["python-aiohttp"],
    })
    description = fields.String(metadata={
        "description": "Package description",
        "example": "ArcH linux ReposItory MANager",
    })
    filename = fields.String(metadata={
        "description": "Package file name",
        "example": "ahriman-2.7.1-1-any.pkg.tar.zst",
    })
    groups = fields.List(fields.String(), metadata={
        "description": "Package groups",
        "example": ["base-devel"],
    })
    installed_size = fields.Integer(metadata={
        "description": "Installed package size in bytes",
        "example": 2047658,
    })
    licenses = fields.List(fields.String(), metadata={
        "description": "Package licenses",
        "example": ["GPL3"],
    })
    provides = fields.List(fields.String(), metadata={
        "description": "Package provides list",
        "example": ["ahriman-git"],
    })
    url = fields.String(metadata={
        "description": "Upstream url",
        "example": "https://github.com/arcan1s/ahriman",
    })
