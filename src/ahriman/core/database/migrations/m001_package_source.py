#
# Copyright (c) 2021-2022 ahriman team.
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
__all__ = ["steps"]


steps = [
    """
    alter table package_bases add column branch text
    """,
    """
    alter table package_bases add column git_url text
    """,
    """
    alter table package_bases add column path text
    """,
    """
    alter table package_bases add column web_url text
    """,
    """
    alter table package_bases add column source text
    """,
    """
    alter table package_bases drop column aur_url
    """,
]
