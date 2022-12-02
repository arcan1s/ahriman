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
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from ahriman.core.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.core.spawn import Spawn
from ahriman.core.status.watcher import Watcher
from ahriman.models.user_access import UserAccess


T = TypeVar("T", str, List[str])


class BaseView(View):
    """
    base web view to make things typed
    """

    @property
    def configuration(self) -> Configuration:
        """
        get configuration instance

        Returns:
            Configuration: configuration instance
        """
        configuration: Configuration = self.request.app["configuration"]
        return configuration

    @property
    def service(self) -> Watcher:
        """
        get status watcher instance

        Returns:
            Watcher: build status watcher instance
        """
        watcher: Watcher = self.request.app["watcher"]
        return watcher

    @property
    def spawner(self) -> Spawn:
        """
        get process spawner instance

        Returns:
            Spawn: external process spawner instance
        """
        spawner: Spawn = self.request.app["spawn"]
        return spawner

    @property
    def validator(self) -> Auth:
        """
        get authorization instance

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
        permission: UserAccess = getattr(cls, f"{request.method.upper()}_PERMISSION", UserAccess.Full)
        return permission

    @staticmethod
    def get_non_empty(extractor: Callable[[str], Optional[T]], key: str) -> T:
        """
        get non-empty value from request parameters

        Args:
            extractor(Callable[[str], T]): function to get value by the specified key
            key(str): key to extract value

        Returns:
            T: extracted values if it is presented and not empty

        Raises:
            KeyError: in case if key was not found or value is empty
        """
        try:
            value = extractor(key)
            if not value:
                raise KeyError(key)
        except Exception:
            raise KeyError(f"Key {key} is missing or empty")
        return value

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
