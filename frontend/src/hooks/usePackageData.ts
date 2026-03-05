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
import { useAutoRefresh } from "hooks/useAutoRefresh";
import { useClient } from "hooks/useClient";
import { useRepository } from "hooks/useRepository";
import type { AutoRefreshInterval } from "models/AutoRefreshInterval";
import type { BuildStatus } from "models/BuildStatus";
import { PackageRow } from "models/PackageRow";
import { useMemo } from "react";
import { defaultInterval } from "utils";

export interface UsePackageDataResult {
    rows: PackageRow[];
    isLoading: boolean;
    isAuthorized: boolean;
    status: BuildStatus | undefined;
    autoRefresh: ReturnType<typeof useAutoRefresh>;
}

export function usePackageData(autoRefreshIntervals: AutoRefreshInterval[]): UsePackageDataResult {
    const client = useClient();
    const { current } = useRepository();
    const { isAuthorized } = useAuth();

    const autoRefresh = useAutoRefresh("table-autoreload-button", defaultInterval(autoRefreshIntervals));

    const { data: packages = [], isLoading } = useQuery({
        queryKey: current ? QueryKeys.packages(current) : ["packages"],
        queryFn: current ? () => client.fetch.fetchPackages(current) : skipToken,
        refetchInterval: autoRefresh.interval > 0 ? autoRefresh.interval : false,
    });

    const { data: status } = useQuery({
        queryKey: current ? QueryKeys.status(current) : ["status"],
        queryFn: current ? () => client.fetch.fetchServerStatus(current) : skipToken,
        refetchInterval: autoRefresh.interval > 0 ? autoRefresh.interval : false,
    });

    const rows = useMemo(() => packages.map(descriptor => new PackageRow(descriptor)), [packages]);

    return {
        rows,
        isLoading,
        isAuthorized,
        status: status?.status.status,
        autoRefresh,
    };
}
