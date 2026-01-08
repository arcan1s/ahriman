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
from sqlite3 import Connection

from ahriman.core.database.operations.operations import Operations
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


class AuthOperations(Operations):
    """
    authorization operations
    """

    def user_get(self, username: str) -> User | None:
        """
        get user by username

        Args:
            username(str): username

        Returns:
            User | None: user if it was found
        """
        return next(iter(self.user_list(username, None)), None)

    def user_list(self, username: str | None, access: UserAccess | None) -> list[User]:
        """
        get users by filter

        Args:
            username(str | None): optional filter by username
            access(UserAccess | None): optional filter by role

        Returns:
            list[User]: list of users who match criteria
        """
        username_filter = username.lower() if username is not None else username
        access_filter = access.value if access is not None else access

        def run(connection: Connection) -> list[User]:
            return [
                User(username=row["username"], password=row["password"], access=UserAccess(row["access"]),
                     packager_id=row["packager_id"], key=row["key_id"])
                for row in connection.execute(
                    """
                    select * from users
                    where (:username is null or username = :username) and (:access is null or access = :access)
                    """,
                    {"username": username_filter, "access": access_filter})
            ]

        return self.with_connection(run)

    def user_remove(self, username: str) -> None:
        """
        remove user from storage

        Args:
            username(str): username
        """
        def run(connection: Connection) -> None:
            connection.execute("""delete from users where username = :username""", {"username": username.lower()})

        return self.with_connection(run, commit=True)

    def user_update(self, user: User) -> None:
        """
        update user by username

        Args:
            user(User): user descriptor
        """
        def run(connection: Connection) -> None:
            connection.execute(
                """
                insert into users
                (username, access, password, packager_id, key_id)
                values
                (:username, :access, :password, :packager_id, :key_id)
                on conflict (username) do update set
                access = :access, password = :password, packager_id = :packager_id, key_id = :key_id
                """,
                {"username": user.username.lower(), "access": user.access.value, "password": user.password,
                 "packager_id": user.packager_id, "key_id": user.key})

        self.with_connection(run, commit=True)
