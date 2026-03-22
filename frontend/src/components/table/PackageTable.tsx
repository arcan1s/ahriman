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
import { Box, Link } from "@mui/material";
import {
    DataGrid,
    GRID_CHECKBOX_SELECTION_COL_DEF,
    type GridColDef,
    type GridFilterModel,
    type GridRowId,
    useGridApiRef,
} from "@mui/x-data-grid";
import DashboardDialog from "components/dialogs/DashboardDialog";
import KeyImportDialog from "components/dialogs/KeyImportDialog";
import PackageAddDialog from "components/dialogs/PackageAddDialog";
import PackageInfoDialog from "components/dialogs/PackageInfoDialog";
import PackageRebuildDialog from "components/dialogs/PackageRebuildDialog";
import PackageTableToolbar from "components/table/PackageTableToolbar";
import StatusCell from "components/table/StatusCell";
import { useDebounce } from "hooks/useDebounce";
import { usePackageTable } from "hooks/usePackageTable";
import type { AutoRefreshInterval } from "models/AutoRefreshInterval";
import type { PackageRow } from "models/PackageRow";
import React, { useMemo } from "react";

interface PackageTableProps {
    autoRefreshIntervals: AutoRefreshInterval[];
}

function createListColumn(
    field: keyof PackageRow,
    headerName: string,
    options: { flex?: number; minWidth?: number; width?: number },
): GridColDef<PackageRow> {
    return {
        field,
        headerName,
        ...options,
        renderCell: params =>
            <Box sx={{ whiteSpace: "pre-line" }}>{((params.row[field] as string[]) ?? []).join("\n")}</Box>,
        sortComparator: (left: string, right: string) => left.localeCompare(right),
        valueGetter: (value: string[]) => (value ?? []).join(" "),
    };
}

export default function PackageTable({ autoRefreshIntervals }: PackageTableProps): React.JSX.Element {
    const table = usePackageTable(autoRefreshIntervals);
    const apiRef = useGridApiRef();
    const debouncedSearch = useDebounce(table.searchText, 300);

    const effectiveFilterModel: GridFilterModel = useMemo(
        () => ({
            ...table.filterModel,
            quickFilterValues: debouncedSearch ? debouncedSearch.split(/\s+/) : undefined,
        }),
        [table.filterModel, debouncedSearch],
    );

    const columns: GridColDef<PackageRow>[] = useMemo(
        () => [
            {
                field: "base",
                flex: 1,
                headerName: "package base",
                minWidth: 150,
                renderCell: params =>
                    params.row.webUrl ?
                        <Link href={params.row.webUrl} rel="noopener noreferrer" target="_blank" underline="hover">
                            {params.value as string}
                        </Link>
                        : params.value as string,
            },
            { align: "right", field: "version", headerAlign: "right", headerName: "version", width: 180 },
            createListColumn("packages", "packages", { flex: 1, minWidth: 120 }),
            createListColumn("groups", "groups", { width: 150 }),
            createListColumn("licenses", "licenses", { width: 150 }),
            { field: "packager", headerName: "packager", width: 150 },
            { align: "right", field: "timestamp", headerName: "last update", headerAlign: "right", width: 180 },
            {
                align: "center",
                field: "status",
                headerAlign: "center",
                headerName: "status",
                renderCell: params =>
                    <StatusCell isHeld={params.row.isHeld} status={params.row.status} />,
                width: 120,
            },
        ],
        [],
    );

    return <Box sx={{ display: "flex", flexDirection: "column", width: "100%" }}>
        <PackageTableToolbar
            actions={{
                onAddClick: () => table.setDialogOpen("add"),
                onDashboardClick: () => table.setDialogOpen("dashboard"),
                onExportClick: () => apiRef.current?.exportDataAsCsv(),
                onKeyImportClick: () => table.setDialogOpen("keyImport"),
                onRebuildClick: () => table.setDialogOpen("rebuild"),
                onRefreshDatabaseClick: () => void table.handleRefreshDatabase(),
                onReloadClick: table.handleReload,
                onRemoveClick: () => void table.handleRemove(),
                onUpdateClick: () => void table.handleUpdate(),
            }}
            autoRefresh={{
                autoRefreshIntervals,
                currentInterval: table.autoRefreshInterval,
                onIntervalChange: table.onAutoRefreshIntervalChange,
            }}
            isAuthorized={table.isAuthorized}
            hasSelection={table.selectionModel.length > 0}
            onSearchChange={table.setSearchText}
            searchText={table.searchText}
            status={table.status}
        />

        <DataGrid
            apiRef={apiRef}
            checkboxSelection
            columnVisibilityModel={table.columnVisibility}
            columns={columns}
            density="compact"
            disableRowSelectionOnClick
            filterModel={effectiveFilterModel}
            getRowHeight={() => "auto"}
            initialState={{
                sorting: { sortModel: [{ field: "base", sort: "asc" }] },
            }}
            loading={table.isLoading}
            onCellClick={(params, event) => {
                // Don't open info dialog when clicking checkbox or link
                if (params.field === GRID_CHECKBOX_SELECTION_COL_DEF.field) {
                    return;
                }
                if ((event.target as HTMLElement).closest("a")) {
                    return;
                }
                table.setSelectedPackage(String(params.id));
            }}
            onColumnVisibilityModelChange={table.setColumnVisibility}
            onFilterModelChange={table.setFilterModel}
            onPaginationModelChange={table.setPaginationModel}
            onRowSelectionModelChange={model => {
                if (model.type === "exclude") {
                    const excludeIds = new Set([...model.ids].map(String));
                    table.setSelectionModel(table.rows.map(row => row.id).filter(id => !excludeIds.has(id)));
                } else {
                    table.setSelectionModel([...model.ids].map(String));
                }
            }}
            paginationModel={table.paginationModel}
            rowSelectionModel={{ type: "include", ids: new Set<GridRowId>(table.selectionModel) }}
            rows={table.rows}
            sx={{ flex: 1 }}
        />

        <DashboardDialog onClose={() => table.setDialogOpen(null)} open={table.dialogOpen === "dashboard"} />
        <PackageAddDialog onClose={() => table.setDialogOpen(null)} open={table.dialogOpen === "add"} />
        <PackageRebuildDialog onClose={() => table.setDialogOpen(null)} open={table.dialogOpen === "rebuild"} />
        <KeyImportDialog onClose={() => table.setDialogOpen(null)} open={table.dialogOpen === "keyImport"} />
        <PackageInfoDialog
            autoRefreshIntervals={autoRefreshIntervals}
            onClose={() => table.setSelectedPackage(null)}
            open={table.selectedPackage !== null}
            packageBase={table.selectedPackage}
        />
    </Box>;
}
