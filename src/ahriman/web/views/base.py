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
from __future__ import annotations

from aiohttp.web import Request, View
from typing import Any, Dict, List, Optional, Type

from ahriman.core.auth.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.core.database.sqlite import SQLite
from ahriman.core.spawn import Spawn
from ahriman.core.status.watcher import Watcher
from ahriman.models.user_access import UserAccess


class BaseView(View):
    """
    base web view to make things typed
    """

    @property
    def configuration(self) -> Configuration:
        """
        Returns:
            Configuration: configuration instance
        """
        configuration: Configuration = self.request.app["configuration"]
        return configuration

    @property
    def database(self) -> SQLite:
        """
        Returns:
            SQLite: database instance
        """
        database: SQLite = self.request.app["database"]
        return database

    @property
    def service(self) -> Watcher:
        """
        Returns:
            Watcher: build status watcher instance
        """
        watcher: Watcher = self.request.app["watcher"]
        return watcher

    @property
    def spawner(self) -> Spawn:
        """
        Returns:
            Spawn: external process spawner instance
        """
        spawner: Spawn = self.request.app["spawn"]
        return spawner

    @property
    def validator(self) -> Auth:
        """
        Returns:
            Auth: authorization service instance
        """
        validator: Auth = self.request.app["validator"]
        return validator

    @classmethod
    async def get_permission(cls: Type[BaseView], request: Request) -> UserAccess:
        """
        retrieve user permission from the request

        Args:
            request(Request): request object

        Returns:
            UserAccess: extracted permission
        """
        permission: UserAccess = getattr(cls, f"{request.method.upper()}_PERMISSION", UserAccess.Write)
        return permission

    async def extract_data(self, list_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        extract json data from either json or form data

        Args:
            list_keys(Optional[List[str]], optional): optional list of keys which must be forced to list from form data
                (Default value = None)

        Returns:
            Dict[str, Any]: raw json object or form data converted to json
        """
        try:
            json: Dict[str, Any] = await self.request.json()
            return json
        except ValueError:
            return await self.data_as_json(list_keys or [])

    async def data_as_json(self, list_keys: List[str]) -> Dict[str, Any]:
        """
        extract form data and convert it to json object

        Args:
            list_keys(List[str]): list of keys which must be forced to list from form data

        Returns:
            Dict[str, Any]: form data converted to json. In case if a key is found multiple times
                it will be returned as list
        """
        raw = await self.request.post()
        json: Dict[str, Any] = {}
        for key, value in raw.items():
            if key in json and isinstance(json[key], list):
                json[key].append(value)
            elif key in json:
                json[key] = [json[key], value]
            elif key in list_keys:
                json[key] = [value]
            else:
                json[key] = value
        return json
