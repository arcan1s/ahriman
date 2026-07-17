#
# Copyright (c) 2021-2026 ahriman team.
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
from ahriman.web.apispec import Schema, fields


class AutoRefreshIntervalSchema(Schema):
    """
    auto refresh interval schema
    """

    interval = fields.Integer(required=True, metadata={
        "description": "Auto refresh interval in milliseconds",
        "example": "60000",
    })
    is_active = fields.Boolean(required=True, metadata={
        "description": "Whether this interval is the default active one",
    })
    text = fields.String(required=True, metadata={
        "description": "Human readable interval description",
        "example": "1 minute",
    })
