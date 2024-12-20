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
from ahriman.models.package_source import PackageSource
from ahriman.web.apispec import Schema, fields


class RemoteSchema(Schema):
    """
    request and response package remote schema
    """

    branch = fields.String(metadata={
        "description": "Repository branch",
        "example": "master",
    })
    git_url = fields.String(metadata={
        "description": "Package git url",
        "example": "https://aur.archlinux.org/ahriman.git",
    })
    path = fields.String(metadata={
        "description": "Path to package sources in git repository",
        "example": ".",
    })
    source = fields.Enum(PackageSource, by_value=True, required=True, metadata={
        "description": "Pacakge source",
    })
    web_url = fields.String(metadata={
        "description": "Package repository page",
        "example": "https://aur.archlinux.org/packages/ahriman",
    })
