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
from ahriman import __version__
from ahriman.web.apispec import fields
from ahriman.web.schemas.counters_schema import CountersSchema
from ahriman.web.schemas.repository_id_schema import RepositoryIdSchema
from ahriman.web.schemas.repository_stats_schema import RepositoryStatsSchema
from ahriman.web.schemas.status_schema import StatusSchema


class InternalStatusSchema(RepositoryIdSchema):
    """
    response service status schema
    """

    packages = fields.Nested(CountersSchema(), required=True, metadata={
        "description": "Repository package counters",
    })
    stats = fields.Nested(RepositoryStatsSchema(), required=True, metadata={
        "description": "Repository stats",
    })
    status = fields.Nested(StatusSchema(), required=True, metadata={
        "description": "Repository status as stored by web service",
    })
    version = fields.String(required=True, metadata={
        "description": "Service version",
        "example": __version__,
    })
