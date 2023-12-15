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
from aiohttp_cors import CorsViewMixin  # type: ignore[import-untyped]
from aiohttp.web import HTTPBadRequest, HTTPNotFound, Request, StreamResponse, View
from collections.abc import Awaitable, Callable
from typing import TypeVar

from ahriman.core.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.core.sign.gpg import GPG
from ahriman.core.spawn import Spawn
from ahriman.core.status.watcher import Watcher
from ahriman.models.repository_id import RepositoryId
from ahriman.models.user_access import UserAccess


T = TypeVar("T", str, list[str])


class BaseView(View, CorsViewMixin):
    """
    base web view to make things typed

    Attributes:
        OPTIONS_PERMISSION(UserAccess): (class attribute) options permissions of self
        ROUTES(list[str]): (class attribute) list of supported routes
    """

    OPTIONS_PERMISSION = UserAccess.Unauthorized
    ROUTES: list[str] = []

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
    def services(self) -> dict[RepositoryId, Watcher]:
        """
        get all loaded watchers

        Returns:
            dict[RepositoryId, Watcher]: map of loaded watchers per known repository
        """
        watchers: dict[RepositoryId, Watcher] = self.request.app["watcher"]
        return watchers

    @property
    def sign(self) -> GPG:
        """
        get GPG control instance

        Returns:
            GPG: GPG wrapper instance
        """
        return GPG(self.configuration)

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
    async def get_permission(cls, request: Request) -> UserAccess:
        """
        retrieve user permission from the request

        Args:
            request(Request): request object

        Returns:
            UserAccess: extracted permission
        """
        method = "GET" if (other := request.method.upper()) == "HEAD" else other
        permission: UserAccess = getattr(cls, f"{method}_PERMISSION", UserAccess.Full)
        return permission

    @classmethod
    def routes(cls, configuration: Configuration) -> list[str]:
        """
        extract routes list for the view

        Args:
            configuration(Configuration): configuration instance

        Returns:
            list[str]: list of routes defined for the view. By default, it tries to read :attr:`ROUTES` option if set
        and returns empty list otherwise
        """
        del configuration
        return cls.ROUTES

    @staticmethod
    def get_non_empty(extractor: Callable[[str], T | None], key: str) -> T:
        """
        get non-empty value from request parameters

        Args:
            extractor(Callable[[str], T | None]): function to get value
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
            raise KeyError(f"Key {key} is missing or empty") from None
        return value

    # pylint: disable=not-callable,protected-access
    async def head(self) -> StreamResponse:
        """
        HEAD method implementation based on the result of GET method

        Raises:
            HTTPMethodNotAllowed: in case if there is no GET method implemented
        """
        get_method: Callable[..., Awaitable[StreamResponse]] | None = getattr(self, "get", None)
        # using if/else in order to suppress mypy warning which doesn't know that
        # :func:`aiohttp.web.View._raise_allowed_methods()` raises exception
        if get_method is not None:
            # there is a bug in pylint, see https://github.com/pylint-dev/pylint/issues/6005
            response = await get_method()
            response._body = b""  # type: ignore[assignment]
            return response

        self._raise_allowed_methods()

    def page(self) -> tuple[int, int]:
        """
        parse limit and offset and return values

        Returns:
            tuple[int, int]: limit and offset from request

        Raises:
            HTTPBadRequest: if supplied parameters are invalid
        """
        try:
            limit = int(self.request.query.get("limit", default=-1))
            offset = int(self.request.query.get("offset", default=0))
        except Exception as ex:
            raise HTTPBadRequest(reason=str(ex))

        # some checks
        if limit < -1:
            raise HTTPBadRequest(reason=f"Limit must be -1 or non-negative, got {limit}")
        if offset < 0:
            raise HTTPBadRequest(reason=f"Offset must be non-negative, got {offset}")

        return limit, offset

    def repository_id(self) -> RepositoryId:
        """
        extract repository from request

        Returns:
            RepositoryIde: repository if possible to construct and first one otherwise
        """
        architecture = self.request.query.get("architecture")
        name = self.request.query.get("repository")

        if architecture and name:
            return RepositoryId(architecture, name)
        return next(iter(sorted(self.services.keys())))

    def service(self, repository_id: RepositoryId | None = None) -> Watcher:
        """
        get status watcher instance

        Args:
            repository_id(RepositoryId | None, optional): repository unique identifier (Default value = None)

        Returns:
            Watcher: build status watcher instance. If no repository provided, it will return the first one

        Raises:
            HTTPNotFound: if no repository found
        """
        if repository_id is None:
            repository_id = self.repository_id()
        try:
            return self.services[repository_id]
        except KeyError:
            raise HTTPNotFound(reason=f"Repository {repository_id.id} is unknown")

    async def username(self) -> str | None:
        """
        extract username from request if any

        Returns:
            str | None: authorized username if any and None otherwise (e.g. if authorization is disabled)
        """
        try:  # try to read from payload
            data: dict[str, str] = await self.request.json()  # technically it is not, but we only need str here
            if (packager := data.get("packager")) is not None:
                return packager
        except Exception:
            self.request.app.logger.exception("could not extract json data for packager")

        policy = self.request.app.get("identity")
        if policy is not None:
            identity: str = await policy.identify(self.request)
            return identity
        return None
