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
import AddIcon from "@mui/icons-material/Add";
import ClearIcon from "@mui/icons-material/Clear";
import DeleteIcon from "@mui/icons-material/Delete";
import DownloadIcon from "@mui/icons-material/Download";
import FileDownloadIcon from "@mui/icons-material/FileDownload";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import InventoryIcon from "@mui/icons-material/Inventory";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import RefreshIcon from "@mui/icons-material/Refresh";
import ReplayIcon from "@mui/icons-material/Replay";
import SearchIcon from "@mui/icons-material/Search";
import VpnKeyIcon from "@mui/icons-material/VpnKey";
import { Box, Button, Divider, IconButton, InputAdornment, Menu, MenuItem, TextField, Tooltip } from "@mui/material";
import AutoRefreshControl from "components/common/AutoRefreshControl";
import type { AutoRefreshInterval } from "models/AutoRefreshInterval";
import type { BuildStatus } from "models/BuildStatus";
import React, { useState } from "react";
import { StatusColors } from "theme/StatusColors";

export interface AutoRefreshProps {
    autoRefreshIntervals: AutoRefreshInterval[];
    currentInterval: number;
    onIntervalChange: (interval: number) => void;
}

export interface ToolbarActions {
    onDashboardClick: () => void;
    onAddClick: () => void;
    onUpdateClick: () => void;
    onRefreshDatabaseClick: () => void;
    onRebuildClick: () => void;
    onRemoveClick: () => void;
    onKeyImportClick: () => void;
    onReloadClick: () => void;
    onExportClick: () => void;
}

interface PackageTableToolbarProps {
    hasSelection: boolean;
    isAuthorized: boolean;
    status?: BuildStatus;
    searchText: string;
    onSearchChange: (text: string) => void;
    autoRefresh: AutoRefreshProps;
    actions: ToolbarActions;
}

export default function PackageTableToolbar({
    hasSelection,
    isAuthorized,
    status,
    searchText,
    onSearchChange,
    autoRefresh,
    actions,
}: PackageTableToolbarProps): React.JSX.Element {
    const [packagesAnchorEl, setPackagesAnchorEl] = useState<HTMLElement | null>(null);

    return <Box sx={{ display: "flex", gap: 1, mb: 1, flexWrap: "wrap", alignItems: "center" }}>
        <Tooltip title="System health">
            <IconButton
                aria-label="System health"
                onClick={actions.onDashboardClick}
                sx={{
                    borderColor: status ? StatusColors[status] : undefined,
                    borderWidth: 1,
                    borderStyle: "solid",
                    color: status ? StatusColors[status] : undefined,
                }}
            >
                <InfoOutlinedIcon />
            </IconButton>
        </Tooltip>

        {isAuthorized &&
            <>
                <Button
                    variant="contained"
                    startIcon={<InventoryIcon />}
                    onClick={event => setPackagesAnchorEl(event.currentTarget)}
                >
                    packages
                </Button>
                <Menu
                    anchorEl={packagesAnchorEl}
                    open={Boolean(packagesAnchorEl)}
                    onClose={() => setPackagesAnchorEl(null)}
                >
                    <MenuItem onClick={() => {
                        setPackagesAnchorEl(null); actions.onAddClick();
                    }}>
                        <AddIcon fontSize="small" sx={{ mr: 1 }} /> add
                    </MenuItem>
                    <MenuItem onClick={() => {
                        setPackagesAnchorEl(null); actions.onUpdateClick();
                    }}>
                        <PlayArrowIcon fontSize="small" sx={{ mr: 1 }} /> update
                    </MenuItem>
                    <MenuItem onClick={() => {
                        setPackagesAnchorEl(null); actions.onRefreshDatabaseClick();
                    }}>
                        <DownloadIcon fontSize="small" sx={{ mr: 1 }} /> update pacman databases
                    </MenuItem>
                    <MenuItem onClick={() => {
                        setPackagesAnchorEl(null); actions.onRebuildClick();
                    }}>
                        <ReplayIcon fontSize="small" sx={{ mr: 1 }} /> rebuild
                    </MenuItem>
                    <Divider />
                    <MenuItem onClick={() => {
                        setPackagesAnchorEl(null); actions.onRemoveClick();
                    }} disabled={!hasSelection}>
                        <DeleteIcon fontSize="small" sx={{ mr: 1 }} /> remove
                    </MenuItem>
                </Menu>

                <Button variant="contained" color="info" startIcon={<VpnKeyIcon />} onClick={actions.onKeyImportClick}>
                    import key
                </Button>
            </>
        }

        <Button variant="outlined" color="secondary" startIcon={<RefreshIcon />} onClick={actions.onReloadClick}>
            reload
        </Button>

        <AutoRefreshControl
            intervals={autoRefresh.autoRefreshIntervals}
            currentInterval={autoRefresh.currentInterval}
            onIntervalChange={autoRefresh.onIntervalChange}
        />

        <Box sx={{ flexGrow: 1 }} />

        <TextField
            size="small"
            aria-label="Search packages"
            placeholder="search packages..."
            value={searchText}
            onChange={event => onSearchChange(event.target.value)}
            slotProps={{
                input: {
                    startAdornment:
                            <InputAdornment position="start">
                                <SearchIcon fontSize="small" />
                            </InputAdornment>
                    ,
                    endAdornment: searchText ?
                        <InputAdornment position="end">
                            <IconButton size="small" aria-label="Clear search" onClick={() => onSearchChange("")}>
                                <ClearIcon fontSize="small" />
                            </IconButton>
                        </InputAdornment>
                        : undefined,
                },
            }}
            sx={{ minWidth: 200 }}
        />

        <Tooltip title="Export CSV">
            <IconButton size="small" aria-label="Export CSV" onClick={actions.onExportClick}>
                <FileDownloadIcon fontSize="small" />
            </IconButton>
        </Tooltip>
    </Box>;
}
