/*
 * Copyright (c) 2021-2026 ahriman team.
 *
 * This file is part of ahriman
 * (see https://github.com/arcan1s/ahriman).
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */
import { ApiError } from "api/client/ApiError";
import type { RequestOptions } from "api/client/RequestOptions";

export class Client {

    private static readonly DEFAULT_TIMEOUT = 30_000;

    async request<T>(url: string, options: RequestOptions = {}): Promise<T> {
        const { method, query, json, timeout = Client.DEFAULT_TIMEOUT } = options;

        let fullUrl = url;
        if (query) {
            const params = new URLSearchParams();
            for (const [key, value] of Object.entries(query)) {
                if (value !== undefined && value !== null) {
                    params.set(key, String(value));
                }
            }
            fullUrl += `?${params.toString()}`;
        }

        const headers: Record<string, string> = {
            Accept: "application/json",
        };
        if (json !== undefined) {
            headers["Content-Type"] = "application/json";
        }

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const requestInit: RequestInit = {
            method: method ?? (json ? "POST" : "GET"),
            headers,
            signal: controller.signal,
        };

        if (json !== undefined) {
            requestInit.body = JSON.stringify(json);
        }

        let response: Response;
        try {
            response = await fetch(fullUrl, requestInit);
        } finally {
            clearTimeout(timeoutId);
        }

        if (!response.ok) {
            const body = await response.text();
            throw new ApiError(response.status, response.statusText, body);
        }

        const contentType = response.headers.get("Content-Type") ?? "";
        if (!contentType.includes("application/json")) {
            return undefined as T;
        }
        return await response.json() as T;
    }
}
