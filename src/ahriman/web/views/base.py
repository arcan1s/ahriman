#
# Copyright (c) 2021 ahriman team.
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
from aiohttp.web import View
from typing import Any, Dict, List, Optional

from ahriman.core.auth.auth import Auth
from ahriman.core.spawn import Spawn
from ahriman.core.status.watcher import Watcher


class BaseView(View):
    """
    base web view to make things typed
    """

    @property
    def service(self) -> Watcher:
        """
        :return: build status watcher instance
        """
        watcher: Watcher = self.request.app["watcher"]
        return watcher

    @property
    def spawner(self) -> Spawn:
        """
        :return: external process spawner instance
        """
        spawner: Spawn = self.request.app["spawn"]
        return spawner

    @property
    def validator(self) -> Auth:
        """
        :return: authorization service instance
        """
        validator: Auth = self.request.app["validator"]
        return validator

    async def extract_data(self, list_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        extract json data from either json or form data
        :param list_keys: optional list of keys which must be forced to list from form data
        :return: raw json object or form data converted to json
        """
        try:
            json: Dict[str, Any] = await self.request.json()
            return json
        except ValueError:
            return await self.data_as_json(list_keys or [])

    async def data_as_json(self, list_keys: List[str]) -> Dict[str, Any]:
        """
        extract form data and convert it to json object
        :param list_keys: list of keys which must be forced to list from form data
        :return: form data converted to json. In case if a key is found multiple times it will be returned as list
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
