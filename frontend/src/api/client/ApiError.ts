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
export class ApiError extends Error {

    body: string;
    status: number;
    statusText: string;

    constructor(status: number, statusText: string, body: string) {
        super(`${status} ${statusText}`);
        this.status = status;
        this.statusText = statusText;
        this.body = body;
    }

    get detail(): string {
        try {
            const parsed = JSON.parse(this.body) as Record<string, string>;
            return parsed.error ?? (this.body || this.message);
        } catch {
            return this.body || this.message;
        }
    }

    static errorDetail(exception: unknown): string {
        return exception instanceof ApiError ? exception.detail : String(exception);
    }
}
