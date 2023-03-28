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


class CountersSchema(Schema):
    """
    response package counters schema
    """

    total = fields.Integer(required=True, metadata={
        "description": "Total amount of packages",
        "example": 6,
    })
    _unknown = fields.Integer(data_key="unknown", required=True, metadata={
        "description": "Amount of packages in unknown state",
        "example": 0,
    })
    pending = fields.Integer(required=True, metadata={
        "description": "Amount of packages in pending state",
        "example": 2,
    })
    building = fields.Integer(required=True, metadata={
        "description": "Amount of packages in building state",
        "example": 1,
    })
    failed = fields.Integer(required=True, metadata={
        "description": "Amount of packages in failed state",
        "example": 1,
    })
    success = fields.Integer(required=True, metadata={
        "description": "Amount of packages in success state",
        "example": 3,
    })
