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
from marshmallow import fields

from ahriman import __version__
from ahriman.web.schemas.repository_id_schema import RepositoryIdSchema


class LogSchema(RepositoryIdSchema):
    """
    request package log schema
    """

    created = fields.Float(required=True, metadata={
        "description": "Log record timestamp",
        "example": 1680537091.233495,
    })
    version = fields.Integer(required=True, metadata={
        "description": "Package version to tag",
        "example": __version__,
    })
    message = fields.String(required=True, metadata={
        "description": "Log message",
    })
