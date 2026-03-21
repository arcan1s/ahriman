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
import { DataGrid, type GridColDef, type GridRenderCellParams } from "@mui/x-data-grid";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError } from "api/client/ApiError";
import { QueryKeys } from "hooks/QueryKeys";
import { useAuth } from "hooks/useAuth";
import { useClient } from "hooks/useClient";
import { useNotification } from "hooks/useNotification";
import type { RepositoryId } from "models/RepositoryId";
import type React from "react";
import { useCallback, useMemo } from "react";

interface ArtifactsTabProps {
    packageBase: string;
    repository: RepositoryId;
    currentVersion: string;
}

interface ArtifactRow {
    id: string;
    version: string;
    packager: string;
    packages: string[];
}

const staticColumns: GridColDef<ArtifactRow>[] = [
    { field: "version", headerName: "version", flex: 1, align: "right", headerAlign: "right" },
    {
        field: "packages",
        headerName: "packages",
        flex: 2,
        renderCell: (params: GridRenderCellParams<ArtifactRow>) =>
            <Box sx={{ whiteSpace: "pre-line" }}>{params.row.packages.join("\n")}</Box>,
    },
    { field: "packager", headerName: "packager", flex: 1 },
];

export default function ArtifactsTab({
    packageBase,
    repository,
    currentVersion,
}: ArtifactsTabProps): React.JSX.Element {
    const client = useClient();
    const queryClient = useQueryClient();
    const { isAuthorized } = useAuth();
    const { showSuccess, showError } = useNotification();

    const { data: rows = [] } = useQuery<ArtifactRow[]>({
        queryKey: QueryKeys.artifacts(packageBase, repository),
        queryFn: async () => {
            const packages = await client.fetch.fetchPackageArtifacts(packageBase, repository);
            return packages.map(artifact => ({
                id: artifact.version,
                version: artifact.version,
                packager: artifact.packager ?? "",
                packages: Object.keys(artifact.packages).sort(),
            })).reverse();
        },
        enabled: !!packageBase,
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
            width: 60,
            renderCell: (params: GridRenderCellParams<ArtifactRow>) =>
                <Tooltip title={params.row.version === currentVersion ? "Current version" : "Rollback to this version"}>
                    <span>
                        <IconButton
                            size="small"
                            disabled={params.row.version === currentVersion}
                            onClick={() => void handleRollback(params.row.version)}
                        >
                            <RestoreIcon fontSize="small" />
                        </IconButton>
                    </span>
                </Tooltip>,
        } satisfies GridColDef<ArtifactRow>] : [],
    ], [isAuthorized, currentVersion, handleRollback]);

    return <Box sx={{ mt: 1 }}>
        <DataGrid
            rows={rows}
            columns={columns}
            density="compact"
            disableColumnSorting
            disableRowSelectionOnClick
            getRowHeight={() => "auto"}
            pageSizeOptions={[10, 25]}
            sx={{ height: 400, mt: 1 }}
        />
    </Box>;
}
