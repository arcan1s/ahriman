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
import type { GridFilterModel } from "@mui/x-data-grid";
import { usePackageActions } from "hooks/usePackageActions";
import { usePackageData } from "hooks/usePackageData";
import { useTableState } from "hooks/useTableState";
import type { AutoRefreshInterval } from "models/AutoRefreshInterval";
import type { BuildStatus } from "models/BuildStatus";
import type { PackageRow } from "models/PackageRow";
import { useEffect } from "react";

export interface UsePackageTableResult {
    rows: PackageRow[];
    isLoading: boolean;
    isAuthorized: boolean;
    status: BuildStatus | undefined;

    selectionModel: string[];
    setSelectionModel: (model: string[]) => void;

    dialogOpen: "dashboard" | "add" | "rebuild" | "keyImport" | null;
    setDialogOpen: (dialog: "dashboard" | "add" | "rebuild" | "keyImport" | null) => void;
    selectedPackage: string | null;
    setSelectedPackage: (base: string | null) => void;

    paginationModel: { pageSize: number; page: number };
    setPaginationModel: (model: { pageSize: number; page: number }) => void;
    columnVisibility: Record<string, boolean>;
    setColumnVisibility: (model: Record<string, boolean>) => void;
    filterModel: GridFilterModel;
    setFilterModel: (model: GridFilterModel) => void;
    searchText: string;
    setSearchText: (text: string) => void;

    autoRefreshInterval: number;
    onAutoRefreshIntervalChange: (interval: number) => void;

    handleReload: () => void;
    handleUpdate: () => Promise<void>;
    handleRefreshDatabase: () => Promise<void>;
    handleRemove: () => Promise<void>;
}

export function usePackageTable(autoRefreshIntervals: AutoRefreshInterval[]): UsePackageTableResult {
    const { rows, isLoading, isAuthorized, status, autoRefresh } = usePackageData(autoRefreshIntervals);
    const tableState = useTableState();
    const actions = usePackageActions(tableState.selectionModel, tableState.setSelectionModel);

    // Pause auto-refresh when dialog is open
    const isDialogOpen = tableState.dialogOpen !== null || tableState.selectedPackage !== null;
    const setPaused = autoRefresh.setPaused;
    useEffect(() => {
        setPaused(isDialogOpen);
    }, [isDialogOpen, setPaused]);

    return {
        rows,
        isLoading,
        isAuthorized,
        status,

        ...tableState,

        autoRefreshInterval: autoRefresh.interval,
        onAutoRefreshIntervalChange: autoRefresh.setInterval,

        ...actions,
    };
}
