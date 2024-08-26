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
from marshmallow import Schema, fields

from ahriman.models.event import EventType


class EventSchema(Schema):
    """
    request/response event schema
    """

    created = fields.Integer(required=True, metadata={
        "description": "Event creation timestamp",
        "example": 1680537091,
    })
    event = fields.String(required=True, metadata={
        "description": "Event type",
        "example": EventType.PackageUpdated,
    })
    object_id = fields.String(required=True, metadata={
        "description": "Event object identifier",
        "example": "ahriman",
    })
    message = fields.String(metadata={
        "description": "Event message if available",
    })
    data = fields.Dict(keys=fields.String(), metadata={
        "description": "Event metadata if available",
    })
