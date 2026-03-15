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
    type GridRenderCellParams,
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

const PAGE_SIZE_OPTIONS = [10, 25, 50, 100];

function createListColumn(
    field: keyof PackageRow,
    headerName: string,
    options: { flex?: number; minWidth?: number; width?: number },
): GridColDef<PackageRow> {
    return {
        field,
        headerName,
        ...options,
        valueGetter: (value: string[]) => (value ?? []).join(" "),
        renderCell: (params: GridRenderCellParams<PackageRow>) =>
            <Box sx={{ whiteSpace: "pre-line" }}>{((params.row[field] as string[]) ?? []).join("\n")}</Box>,
        sortComparator: (left: string, right: string) => left.localeCompare(right),
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
                headerName: "package base",
                flex: 1,
                minWidth: 150,
                renderCell: (params: GridRenderCellParams<PackageRow>) =>
                    params.row.webUrl ?
                        <Link href={params.row.webUrl} target="_blank" rel="noopener noreferrer" underline="hover">
                            {params.value as string}
                        </Link>
                        : params.value as string,
            },
            { field: "version", headerName: "version", width: 180, align: "right", headerAlign: "right" },
            createListColumn("packages", "packages", { flex: 1, minWidth: 120 }),
            createListColumn("groups", "groups", { width: 150 }),
            createListColumn("licenses", "licenses", { width: 150 }),
            { field: "packager", headerName: "packager", width: 150 },
            {
                field: "timestamp",
                headerName: "last update",
                width: 180,
                align: "right",
                headerAlign: "right",
            },
            {
                field: "status",
                headerName: "status",
                width: 120,
                align: "center",
                headerAlign: "center",
                renderCell: (params: GridRenderCellParams<PackageRow>) =>
                    <StatusCell status={params.row.status} isHeld={params.row.isHeld} />,
            },
        ],
        [],
    );

    return <Box sx={{ display: "flex", flexDirection: "column", width: "100%" }}>
        <PackageTableToolbar
            hasSelection={table.selectionModel.length > 0}
            isAuthorized={table.isAuthorized}
            status={table.status}
            searchText={table.searchText}
            onSearchChange={table.setSearchText}
            autoRefresh={{
                autoRefreshIntervals,
                currentInterval: table.autoRefreshInterval,
                onIntervalChange: table.onAutoRefreshIntervalChange,
            }}
            actions={{
                onDashboardClick: () => table.setDialogOpen("dashboard"),
                onAddClick: () => table.setDialogOpen("add"),
                onUpdateClick: () => void table.handleUpdate(),
                onRefreshDatabaseClick: () => void table.handleRefreshDatabase(),
                onRebuildClick: () => table.setDialogOpen("rebuild"),
                onRemoveClick: () => void table.handleRemove(),
                onKeyImportClick: () => table.setDialogOpen("keyImport"),
                onReloadClick: table.handleReload,
                onExportClick: () => apiRef.current?.exportDataAsCsv(),
            }}
        />

        <DataGrid
            apiRef={apiRef}
            rows={table.rows}
            columns={columns}
            loading={table.isLoading}
            getRowHeight={() => "auto"}
            checkboxSelection
            disableRowSelectionOnClick
            rowSelectionModel={{ type: "include", ids: new Set<GridRowId>(table.selectionModel) }}
            onRowSelectionModelChange={model => {
                if (model.type === "exclude") {
                    const excludeIds = new Set([...model.ids].map(String));
                    table.setSelectionModel(table.rows.map(row => row.id).filter(id => !excludeIds.has(id)));
                } else {
                    table.setSelectionModel([...model.ids].map(String));
                }
            }}
            paginationModel={table.paginationModel}
            onPaginationModelChange={table.setPaginationModel}
            pageSizeOptions={PAGE_SIZE_OPTIONS}
            columnVisibilityModel={table.columnVisibility}
            onColumnVisibilityModelChange={table.setColumnVisibility}
            filterModel={effectiveFilterModel}
            onFilterModelChange={table.setFilterModel}
            initialState={{
                sorting: { sortModel: [{ field: "base", sort: "asc" }] },
            }}
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
            sx={{
                flex: 1,
                "& .MuiDataGrid-row": { cursor: "pointer" },
            }}
            density="compact"
        />

        <DashboardDialog open={table.dialogOpen === "dashboard"} onClose={() => table.setDialogOpen(null)} />
        <PackageAddDialog open={table.dialogOpen === "add"} onClose={() => table.setDialogOpen(null)} />
        <PackageRebuildDialog open={table.dialogOpen === "rebuild"} onClose={() => table.setDialogOpen(null)} />
        <KeyImportDialog open={table.dialogOpen === "keyImport"} onClose={() => table.setDialogOpen(null)} />
        <PackageInfoDialog
            packageBase={table.selectedPackage}
            open={table.selectedPackage !== null}
            onClose={() => table.setSelectedPackage(null)}
            autoRefreshIntervals={autoRefreshIntervals}
        />
    </Box>;
}
