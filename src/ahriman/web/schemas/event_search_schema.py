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
from ahriman.models.event import EventType
from ahriman.web.apispec import fields
from ahriman.web.schemas.pagination_schema import PaginationSchema


class EventSearchSchema(PaginationSchema):
    """
    request event search schema
    """

    event = fields.String(metadata={
        "description": "Event type",
        "example": EventType.PackageUpdated,
    })
    object_id = fields.String(metadata={
        "description": "Event object identifier",
        "example": "ahriman",
    })
    from_date = fields.Integer(metadata={
        "description": "Minimal creation timestamp, inclusive",
        "example": 1680537091,
    })
    to_date = fields.Integer(metadata={
        "description": "Maximal creation timestamp, exclusive",
        "example": 1680537091,
    })
