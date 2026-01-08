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
__all__ = ["steps"]


steps = [
    """
    alter table packages rename to packages_
    """,
    """
    create table packages (
        package text not null,
        package_base text not null,
        architecture text not null,
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
        make_depends json,
        opt_depends json,
        unique (package, architecture)
    )
    """,
    """
    insert into packages select * from packages_ where architecture is not null
    """,
    """
    drop table packages_
    """,
]
