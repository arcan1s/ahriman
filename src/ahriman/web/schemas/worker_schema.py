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


class WorkerSchema(Schema):
    """
    request and response schema for workers
    """

    address = fields.String(required=True, metadata={
        "description": "Worker address",
        "example": "http://localhost:8081",
    })
    identifier = fields.String(required=True, metadata={
        "description": "Worker unique identifier",
        "example": "42f03a62-48f7-46b7-af40-dacc720e92fa",
    })
