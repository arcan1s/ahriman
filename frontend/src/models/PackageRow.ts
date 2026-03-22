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
import type { BuildStatus } from "models/BuildStatus";
import type { PackageStatus } from "models/PackageStatus";

export class PackageRow {

    base: string;
    groups: string[];
    id: string;
    isHeld: boolean;
    licenses: string[];
    packager: string;
    packages: string[];
    status: BuildStatus;
    timestamp: string;
    version: string;
    webUrl?: string;

    constructor(descriptor: PackageStatus) {
        this.base = descriptor.package.base;
        this.groups = PackageRow.extractListProperties(descriptor.package, "groups");
        this.id = descriptor.package.base;
        this.isHeld = descriptor.status.is_held ?? false;
        this.licenses = PackageRow.extractListProperties(descriptor.package, "licenses");
        this.packager = descriptor.package.packager ?? "";
        this.packages = Object.keys(descriptor.package.packages).sort();
        this.status = descriptor.status.status;
        this.timestamp = new Date(descriptor.status.timestamp * 1000).toISOStringShort();
        this.version = descriptor.package.version;
        this.webUrl = descriptor.package.remote.web_url ?? undefined;
    }

    private static extractListProperties(pkg: PackageStatus["package"], property: "groups" | "licenses"): string[] {
        return [
            ...new Set(
                Object.values(pkg.packages)
                    .flatMap(properties => properties[property] ?? []),
            ),
        ].sort();
    }
}
