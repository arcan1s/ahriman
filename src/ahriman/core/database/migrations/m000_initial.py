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
__all__ = ["steps"]


steps = [
    """
    create table build_queue (
        package_base text not null unique,
        properties json not null
    )
    """,
    """
    create table package_bases (
        package_base text not null unique,
        version text not null,
        aur_url text not null
    )
    """,
    """
    create table package_statuses (
        package_base text not null unique,
        status text not null,
        last_updated integer
    )
    """,
    """
    create table packages (
        package text not null,
        package_base text not null,
        architecture text,
        archive_size integer,
        build_date integer,
        depends json,
        description text,
        filename text,
        "groups" json,
        installed_size integer,
        licenses json,
        provides json,
        url text,
        unique (package, architecture)
    )
    """,
    """
    create table patches (
        package_base text not null unique,
        patch blob not null
    )
    """,
    """
    create table users (
        username text not null unique,
        access text not null,
        password text
    )
    """,
]
