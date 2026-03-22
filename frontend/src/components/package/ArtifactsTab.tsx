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
import RestoreIcon from "@mui/icons-material/Restore";
import { Box, IconButton, Tooltip } from "@mui/material";
import { DataGrid, type GridColDef } from "@mui/x-data-grid";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError } from "api/client/ApiError";
import { QueryKeys } from "hooks/QueryKeys";
import { useAuth } from "hooks/useAuth";
import { useClient } from "hooks/useClient";
import { useNotification } from "hooks/useNotification";
import type { RepositoryId } from "models/RepositoryId";
import type React from "react";
import { useCallback, useMemo } from "react";
import { DETAIL_TABLE_PROPS } from "utils";

interface ArtifactsTabProps {
    currentVersion: string;
    packageBase: string;
    repository: RepositoryId;
}

interface ArtifactRow {
    id: string;
    packager: string;
    packages: string[];
    version: string;
}

const staticColumns: GridColDef<ArtifactRow>[] = [
    { align: "right", field: "version", flex: 1, headerAlign: "right", headerName: "version" },
    {
        field: "packages",
        flex: 2,
        headerName: "packages",
        renderCell: params =>
            <Box sx={{ whiteSpace: "pre-line" }}>{params.row.packages.join("\n")}</Box>,
    },
    { field: "packager", flex: 1, headerName: "packager" },
];

export default function ArtifactsTab({
    currentVersion,
    packageBase,
    repository,
}: ArtifactsTabProps): React.JSX.Element {
    const client = useClient();
    const queryClient = useQueryClient();
    const { isAuthorized } = useAuth();
    const { showSuccess, showError } = useNotification();

    const { data: rows = [] } = useQuery<ArtifactRow[]>({
        enabled: !!packageBase,
        queryFn: async () => {
            const packages = await client.fetch.fetchPackageArtifacts(packageBase, repository);
            return packages.map(artifact => ({
                id: artifact.version,
                packager: artifact.packager ?? "",
                packages: Object.keys(artifact.packages).sort(),
                version: artifact.version,
            })).reverse();
        },
        queryKey: QueryKeys.artifacts(packageBase, repository),
    });

    const handleRollback = useCallback(async (version: string): Promise<void> => {
        try {
            await client.service.servicePackageRollback(repository, { package: packageBase, version });
            void queryClient.invalidateQueries({ queryKey: QueryKeys.artifacts(packageBase, repository) });
            void queryClient.invalidateQueries({ queryKey: QueryKeys.package(packageBase, repository) });
            showSuccess("Success", `Rollback ${packageBase} to ${version} has been started`);
        } catch (exception) {
            showError("Action failed", `Rollback failed: ${ApiError.errorDetail(exception)}`);
        }
    }, [client, repository, packageBase, queryClient, showSuccess, showError]);

    const columns = useMemo<GridColDef<ArtifactRow>[]>(() => [
        ...staticColumns,
        ...isAuthorized ? [{
            field: "actions",
            filterable: false,
            headerName: "",
            renderCell: params =>
                <Tooltip title={params.row.version === currentVersion ? "Current version" : "Rollback to this version"}>
                    <span>
                        <IconButton
                            disabled={params.row.version === currentVersion}
                            onClick={() => void handleRollback(params.row.version)}
                            size="small"
                        >
                            <RestoreIcon fontSize="small" />
                        </IconButton>
                    </span>
                </Tooltip>,
            width: 60,
        } satisfies GridColDef<ArtifactRow>] : [],
    ], [isAuthorized, currentVersion, handleRollback]);

    return <Box sx={{ mt: 1 }}>
        <DataGrid columns={columns} getRowHeight={() => "auto"} rows={rows} {...DETAIL_TABLE_PROPS} />
    </Box>;
}
