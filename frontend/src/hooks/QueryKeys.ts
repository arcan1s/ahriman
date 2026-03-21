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
import type { RepositoryId } from "models/RepositoryId";

export const QueryKeys = {

    artifacts: (packageBase: string, repository: RepositoryId) => ["artifacts", repository.key, packageBase] as const,

    changes: (packageBase: string, repository: RepositoryId) => ["changes", repository.key, packageBase] as const,

    dependencies: (packageBase: string, repository: RepositoryId) => ["dependencies", repository.key, packageBase] as const,

    events: (repository: RepositoryId, objectId?: string) => ["events", repository.key, objectId] as const,

    info: ["info"] as const,

    logs: (packageBase: string, repository: RepositoryId) => ["logs", repository.key, packageBase] as const,

    logsVersion: (packageBase: string, repository: RepositoryId, version: string, processId: string) =>
        ["logs", repository.key, packageBase, version, processId] as const,

    package: (packageBase: string, repository: RepositoryId) => ["packages", repository.key, packageBase] as const,

    packages: (repository: RepositoryId) => ["packages", repository.key] as const,

    patches: (packageBase: string) => ["patches", packageBase] as const,

    search: (query: string) => ["search", query] as const,

    status: (repository: RepositoryId) => ["status", repository.key] as const,
};
