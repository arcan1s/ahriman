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
import { useLocalStorage } from "hooks/useLocalStorage";
import { useState } from "react";

export type DialogType = "dashboard" | "add" | "rebuild" | "keyImport";

export interface UseTableStateResult {
    columnVisibility: Record<string, boolean>;
    dialogOpen: DialogType | null;
    filterModel: GridFilterModel;
    paginationModel: { pageSize: number; page: number };
    searchText: string;
    selectedPackage: string | null;
    selectionModel: string[];
    setColumnVisibility: (model: Record<string, boolean>) => void;
    setDialogOpen: (dialog: DialogType | null) => void;
    setFilterModel: (model: GridFilterModel) => void;
    setPaginationModel: (model: { pageSize: number; page: number }) => void;
    setSearchText: (text: string) => void;
    setSelectedPackage: (base: string | null) => void;
    setSelectionModel: (model: string[]) => void;
}

export function useTableState(): UseTableStateResult {
    const [selectionModel, setSelectionModel] = useState<string[]>([]);
    const [dialogOpen, setDialogOpen] = useState<DialogType | null>(null);
    const [selectedPackage, setSelectedPackage] = useState<string | null>(null);
    const [searchText, setSearchText] = useState("");

    const [paginationModel, setPaginationModel] = useLocalStorage("ahriman-packages-pagination", {
        page: 0,
        pageSize: 25,
    });
    const [columnVisibility, setColumnVisibility] = useLocalStorage<Record<string, boolean>>(
        "ahriman-packages-columns",
        { groups: false, licenses: false, packager: false },
    );
    const [filterModel, setFilterModel] = useLocalStorage<GridFilterModel>(
        "ahriman-packages-filters",
        { items: [] },
    );

    return {
        columnVisibility,
        dialogOpen,
        filterModel,
        paginationModel,
        searchText,
        selectedPackage,
        selectionModel,
        setColumnVisibility,
        setDialogOpen,
        setFilterModel,
        setPaginationModel,
        setSearchText,
        setSelectedPackage,
        setSelectionModel,
    };
}
