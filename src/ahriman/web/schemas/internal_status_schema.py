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

from ahriman import version
from ahriman.web.schemas.counters_schema import CountersSchema
from ahriman.web.schemas.status_schema import StatusSchema


class InternalStatusSchema(Schema):
    """
    response service status schema
    """

    architecture = fields.String(required=True, metadata={
        "description": "Repository architecture",
        "example": "x86_64",
    })
    packages = fields.Nested(CountersSchema(), required=True, metadata={
        "description": "Repository package counters",
    })
    repository = fields.String(required=True, metadata={
        "description": "Repository name",
        "example": "repo-clone",
    })
    status = fields.Nested(StatusSchema(), required=True, metadata={
        "description": "Repository status as stored by web service",
    })
    version = fields.String(required=True, metadata={
        "description": "Repository version",
        "example": version.__version__,
    })
