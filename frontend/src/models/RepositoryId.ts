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
export class RepositoryId {
    readonly architecture: string;
    readonly repository: string;

    constructor(architecture: string, repository: string) {
        this.architecture = architecture;
        this.repository = repository;
    }

    get key(): string {
        return `${this.architecture}-${this.repository}`;
    }

    get label(): string {
        return `${this.repository} (${this.architecture})`;
    }

    toQuery(): Record<string, string> {
        return { architecture: this.architecture, repository: this.repository };
    }
}
