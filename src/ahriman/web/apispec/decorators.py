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
from aiohttp.web import HTTPException
from typing import Any, Callable

from ahriman.models.user_access import UserAccess
from ahriman.web.apispec import Schema, aiohttp_apispec
from ahriman.web.schemas import AuthSchema, ErrorSchema


__all__ = ["apidocs"]


def _response_schema(response: Schema | type[Schema] | None, response_code: type[HTTPException] | None = None,
                     error_400_enabled: bool = False, error_403_enabled: bool = True,
                     error_404_description: str | None = None) -> dict[int, Any]:
    """
    render response schema specification

    Args:
        response(Schema | type[Schema] | None): response schema type, set ``None`` for empty responses
        response_code(type[HTTPException] | None, optional): code for the success response. If none set it will be
            defined automatically (Default value = None)
        error_400_enabled(bool, optional): include response for 404 codes (Default value = False)
        error_403_enabled(bool, optional): include response for 403 codes (Default value = False)
        error_404_description(str | None, optional): description for 404 codes if available (Default value = None)

    Returns:
        dict[int, Any]: response schema in apispec format
    """
    schema = {
        401: {"description": "Authorization required", "schema": ErrorSchema},
        500: {"description": "Internal server error", "schema": ErrorSchema},
    }

    match response_code:
        case None if response is None:
            code = 204
        case None:
            code = 200
        case exception:
            code = exception.status_code
    schema[code] = {"description": "Success response"}
    if response is not None:
        schema[code]["schema"] = response

    if error_400_enabled:
        schema[400] = {"description": "Bad request", "schema": ErrorSchema}

    if error_403_enabled:
        schema[403] = {"description": "Access is forbidden", "schema": ErrorSchema}

    if error_404_description is not None:
        schema[404] = {"description": error_404_description, "schema": ErrorSchema}

    return schema


def apidocs(*,
            tags: list[str],
            summary: str,
            description: str,
            permission: UserAccess,
            response_code: type[HTTPException] | None = None,
            error_400_enabled: bool = False,
            error_404_description: str | None = None,
            schema: Schema | type[Schema] | None = None,
            match_schema: Schema | type[Schema] | None = None,
            query_schema: Schema | type[Schema] | None = None,
            body_schema: Schema | type[Schema] | None = None,
            body_location: str = "json",
            ) -> Callable[..., Any]:
    """
    wrapper around :mod:`aiohttp_apispec` to decorate HTTP methods

    Args:
        tags(list[str]): list of tags for the endpoint
        summary(str): summary for the endpoint
        description(str): long description for the endpoint
        permission(UserAccess): permission to access endpoint
        response_code(type[HTTPException] | None, optional): code for the success response. If none set it will be
            defined automatically (Default value = None)
        error_400_enabled(bool, optional): include response for 404 codes (Default value = False)
        error_404_description(str | None, optional): description for 404 codes if available (Default value = None)
        schema(Schema | type[Schema] | None): response schema type, set ``None`` for empty responses
            (Default value = None)
        match_schema(Schema | type[Schema] | None): schema for uri matcher if used (Default value = None)
        query_schema(Schema | type[Schema] | None): query string schema type, set ``None`` if not applicable
            (Default value = None)
        body_schema(Schema | type[Schema] | None): body schema type, set ``None`` if not applicable
            (Default value = None)
        body_location(str, optional): body location name (Default value = "json")

    Returns:
        Callable[..., Any]: decorated function
    """
    authorization_required = permission != UserAccess.Unauthorized

    def wrapper(handler: Callable[..., Any]) -> Callable[..., Any]:
        if aiohttp_apispec is None:
            return handler  # apispec is disabled

        responses = _response_schema(
            response=schema,
            response_code=response_code,
            error_400_enabled=error_400_enabled,
            error_403_enabled=authorization_required,
            error_404_description=error_404_description,
        )
        handler = aiohttp_apispec.docs(
            tags=tags,
            summary=summary,
            description=description,
            responses=responses,
            security=[{"token": [permission]}],
        )(handler)

        # request schemas
        if authorization_required:
            handler = aiohttp_apispec.cookies_schema(AuthSchema)(handler)
        if match_schema is not None:
            handler = aiohttp_apispec.match_info_schema(match_schema)(handler)
        if query_schema is not None:
            handler = aiohttp_apispec.querystring_schema(query_schema)(handler)
        if body_schema is not None:
            handler = aiohttp_apispec.request_schema(
                body_schema, locations=[body_location], put_into=body_location)(handler)

        return handler

    return wrapper
