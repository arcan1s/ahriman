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
import type { AURPackage } from "models/AURPackage";
import type { PackageActionRequest } from "models/PackageActionRequest";
import type { PGPKey } from "models/PGPKey";
import type { PGPKeyRequest } from "models/PGPKeyRequest";
import type { RepositoryId } from "models/RepositoryId";
import type { RollbackRequest } from "models/RollbackRequest";

export class ServiceClient {

    protected client: Client;

    constructor(client: Client) {
        this.client = client;
    }

    async servicePackageAdd(repository: RepositoryId, data: PackageActionRequest): Promise<void> {
        return this.client.request("/api/v1/service/add", { method: "POST", query: repository.toQuery(), json: data });
    }

    async servicePackagePatchRemove(packageBase: string, key: string): Promise<void> {
        return this.client.request(`/api/v1/packages/${encodeURIComponent(packageBase)}/patches/${encodeURIComponent(key)}`, {
            method: "DELETE",
        });
    }

    async servicePackageRollback(repository: RepositoryId, data: RollbackRequest): Promise<void> {
        return this.client.request("/api/v1/service/rollback", {
            method: "POST",
            query: repository.toQuery(),
            json: data,
        });
    }

    async servicePackageRemove(repository: RepositoryId, packages: string[]): Promise<void> {
        return this.client.request("/api/v1/service/remove", {
            method: "POST",
            query: repository.toQuery(),
            json: { packages },
        });
    }

    async servicePackageRequest(repository: RepositoryId, data: PackageActionRequest): Promise<void> {
        return this.client.request("/api/v1/service/request", {
            method: "POST",
            query: repository.toQuery(),
            json: data,
        });
    }

    async servicePackageSearch(query: string): Promise<AURPackage[]> {
        return this.client.request<AURPackage[]>("/api/v1/service/search", { query: { for: query } });
    }

    async servicePackageUpdate(repository: RepositoryId, data: PackageActionRequest): Promise<void> {
        return this.client.request("/api/v1/service/update", {
            method: "POST",
            query: repository.toQuery(),
            json: data,
        });
    }

    async servicePGPFetch(key: string, server: string): Promise<PGPKey> {
        return this.client.request<PGPKey>("/api/v1/service/pgp", { query: { key, server } });
    }

    async servicePGPImport(data: PGPKeyRequest): Promise<void> {
        return this.client.request("/api/v1/service/pgp", { method: "POST", json: data });
    }

    async servicePackageHoldUpdate(packageBase: string, repository: RepositoryId, isHeld: boolean): Promise<void> {
        return this.client.request(`/api/v1/packages/${encodeURIComponent(packageBase)}/hold`, {
            method: "POST",
            query: repository.toQuery(),
            json: { is_held: isHeld },
        });
    }

    async serviceRebuild(repository: RepositoryId, packages: string[]): Promise<void> {
        return this.client.request("/api/v1/service/rebuild", {
            method: "POST",
            query: repository.toQuery(),
            json: { packages },
        });
    }
}
