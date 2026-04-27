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
import { skipToken, useQuery } from "@tanstack/react-query";
import { QueryKeys } from "hooks/QueryKeys";
import { useAuth } from "hooks/useAuth";
import { useClient } from "hooks/useClient";
import { useRepository } from "hooks/useRepository";
import type { BuildStatus } from "models/BuildStatus";
import { PackageRow } from "models/PackageRow";
import { useMemo } from "react";

export interface UsePackageDataResult {
    isAuthorized: boolean;
    isLoading: boolean;
    rows: PackageRow[];
    status: BuildStatus | undefined;
}

export function usePackageData(): UsePackageDataResult {
    const client = useClient();
    const { currentRepository } = useRepository();
    const { isAuthorized } = useAuth();

    const { data: packages = [], isLoading } = useQuery({
        queryFn: currentRepository ? () => client.fetch.fetchPackages(currentRepository) : skipToken,
        queryKey: currentRepository ? QueryKeys.packages(currentRepository) : ["packages"],
    });

    const { data: status } = useQuery({
        queryFn: currentRepository ? () => client.fetch.fetchServerStatus(currentRepository) : skipToken,
        queryKey: currentRepository ? QueryKeys.status(currentRepository) : ["status"],
    });

    const rows = useMemo(() => packages.map(descriptor => new PackageRow(descriptor)), [packages]);

    return {
        isLoading,
        isAuthorized,
        rows,
        status: status?.status.status,
    };
}
