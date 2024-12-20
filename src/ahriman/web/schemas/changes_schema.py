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
from ahriman.web.apispec import Schema, fields


class ChangesSchema(Schema):
    """
    response package changes schema
    """

    last_commit_sha = fields.String(metadata={
        "description": "Last recorded commit hash",
        "example": "f1875edca1eb8fc0e55c41d1cae5fa05b6b7c6",
    })
    changes = fields.String(metadata={
        "description": "Package changes in patch format",
    })
