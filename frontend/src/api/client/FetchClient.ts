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
import type { Client } from "api/client/Client";
import type { Changes } from "models/Changes";
import type { Dependencies } from "models/Dependencies";
import type { Event } from "models/Event";
import type { InfoResponse } from "models/InfoResponse";
import type { InternalStatus } from "models/InternalStatus";
import type { LogRecord } from "models/LogRecord";
import type { PackageStatus } from "models/PackageStatus";
import type { Patch } from "models/Patch";
import { RepositoryId } from "models/RepositoryId";

export class FetchClient {

    protected client: Client;

    constructor(client: Client) {
        this.client = client;
    }

    async fetchPackage(packageBase: string, repository: RepositoryId): Promise<PackageStatus[]> {
        return this.client.request<PackageStatus[]>(`/api/v1/packages/${encodeURIComponent(packageBase)}`, {
            query: repository.toQuery(),
        });
    }

    async fetchPackageChanges(packageBase: string, repository: RepositoryId): Promise<Changes> {
        return this.client.request<Changes>(`/api/v1/packages/${encodeURIComponent(packageBase)}/changes`, {
            query: repository.toQuery(),
        });
    }

    async fetchPackageDependencies(packageBase: string, repository: RepositoryId): Promise<Dependencies> {
        return this.client.request<Dependencies>(`/api/v1/packages/${encodeURIComponent(packageBase)}/dependencies`, {
            query: repository.toQuery(),
        });
    }

    async fetchPackageEvents(repository: RepositoryId, objectId?: string, limit?: number): Promise<Event[]> {
        const query: Record<string, string | number> = repository.toQuery();
        if (objectId) {
            query.object_id = objectId;
        }
        if (limit) {
            query.limit = limit;
        }
        return this.client.request<Event[]>("/api/v1/events", { query });
    }

    async fetchPackageLogs(
        packageBase: string,
        repository: RepositoryId,
        version?: string,
        processId?: string,
        head?: boolean,
    ): Promise<LogRecord[]> {
        const query: Record<string, string | boolean> = { ...repository.toQuery() };
        if (version) {
            query.version = version;
        }
        if (processId) {
            query.process_id = processId;
        }
        if (head) {
            query.head = true;
        }
        return this.client.request<LogRecord[]>(`/api/v2/packages/${encodeURIComponent(packageBase)}/logs`, { query });
    }

    async fetchPackagePatches(packageBase: string): Promise<Patch[]> {
        return this.client.request<Patch[]>(`/api/v1/packages/${encodeURIComponent(packageBase)}/patches`);
    }

    async fetchPackages(repository: RepositoryId): Promise<PackageStatus[]> {
        return this.client.request<PackageStatus[]>("/api/v1/packages", { query: repository.toQuery() });
    }

    async fetchServerInfo(): Promise<InfoResponse> {
        const info = await this.client.request<InfoResponse>("/api/v2/info");
        return {
            ...info,
            repositories: info.repositories.map(repo =>
                new RepositoryId(repo.architecture, repo.repository),
            ),
        };
    }

    async fetchServerStatus(repository: RepositoryId): Promise<InternalStatus> {
        return this.client.request<InternalStatus>("/api/v1/status", { query: repository.toQuery() });
    }
}
