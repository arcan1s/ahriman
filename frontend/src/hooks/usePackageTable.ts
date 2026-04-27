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
import type { BuildStatus } from "models/BuildStatus";
import type { PackageRow } from "models/PackageRow";

export interface UsePackageTableResult {
    columnVisibility: Record<string, boolean>;
    dialogOpen: "dashboard" | "add" | "rebuild" | "keyImport" | null;
    filterModel: GridFilterModel;
    handleRefreshDatabase: () => Promise<void>;
    handleReload: () => void;
    handleRemove: () => Promise<void>;
    handleUpdate: () => Promise<void>;
    isAuthorized: boolean;
    isLoading: boolean;
    paginationModel: { page: number; pageSize: number };
    rows: PackageRow[];
    searchText: string;
    selectedPackage: string | null;
    selectionModel: string[];
    setColumnVisibility: (model: Record<string, boolean>) => void;
    setDialogOpen: (dialog: "dashboard" | "add" | "rebuild" | "keyImport" | null) => void;
    setFilterModel: (model: GridFilterModel) => void;
    setPaginationModel: (model: { page: number; pageSize: number }) => void;
    setSearchText: (text: string) => void;
    setSelectedPackage: (base: string | null) => void;
    setSelectionModel: (model: string[]) => void;
    status: BuildStatus | undefined;
}

export function usePackageTable(): UsePackageTableResult {
    const { rows, isLoading, isAuthorized, status } = usePackageData();
    const tableState = useTableState();
    const actions = usePackageActions(tableState.selectionModel, tableState.setSelectionModel);

    return {
        isLoading,
        isAuthorized,
        rows,
        status,
        ...actions,
        ...tableState,
    };
}
