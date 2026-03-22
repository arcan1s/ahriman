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
    onAddClick: () => void;
    onDashboardClick: () => void;
    onExportClick: () => void;
    onKeyImportClick: () => void;
    onRebuildClick: () => void;
    onRefreshDatabaseClick: () => void;
    onReloadClick: () => void;
    onRemoveClick: () => void;
    onUpdateClick: () => void;
}

interface PackageTableToolbarProps {
    actions: ToolbarActions;
    autoRefresh: AutoRefreshProps;
    hasSelection: boolean;
    isAuthorized: boolean;
    onSearchChange: (text: string) => void;
    searchText: string;
    status?: BuildStatus;
}

export default function PackageTableToolbar({
    actions,
    autoRefresh,
    hasSelection,
    isAuthorized,
    onSearchChange,
    searchText,
    status,
}: PackageTableToolbarProps): React.JSX.Element {
    const [packagesAnchorEl, setPackagesAnchorEl] = useState<HTMLElement | null>(null);

    return <Box sx={{ alignItems: "center", display: "flex", flexWrap: "wrap", gap: 1, mb: 1 }}>
        <Tooltip title="System health">
            <IconButton
                aria-label="System health"
                onClick={actions.onDashboardClick}
                sx={{
                    borderColor: status ? StatusColors[status] : undefined,
                    borderStyle: "solid",
                    borderWidth: 1,
                    color: status ? StatusColors[status] : undefined,
                }}
            >
                <InfoOutlinedIcon />
            </IconButton>
        </Tooltip>

        {isAuthorized &&
            <>
                <Button
                    onClick={event => setPackagesAnchorEl(event.currentTarget)}
                    startIcon={<InventoryIcon />}
                    variant="contained"
                >
                    packages
                </Button>
                <Menu
                    anchorEl={packagesAnchorEl}
                    onClose={() => setPackagesAnchorEl(null)}
                    open={Boolean(packagesAnchorEl)}
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
                    <MenuItem disabled={!hasSelection} onClick={() => {
                        setPackagesAnchorEl(null); actions.onRemoveClick();
                    }}>
                        <DeleteIcon fontSize="small" sx={{ mr: 1 }} /> remove
                    </MenuItem>
                </Menu>

                <Button color="info" onClick={actions.onKeyImportClick} startIcon={<VpnKeyIcon />} variant="contained">
                    import key
                </Button>
            </>
        }

        <Button color="secondary" onClick={actions.onReloadClick} startIcon={<RefreshIcon />} variant="outlined">
            reload
        </Button>

        <AutoRefreshControl
            currentInterval={autoRefresh.currentInterval}
            intervals={autoRefresh.autoRefreshIntervals}
            onIntervalChange={autoRefresh.onIntervalChange}
        />

        <Box sx={{ flexGrow: 1 }} />

        <TextField
            aria-label="Search packages"
            onChange={event => onSearchChange(event.target.value)}
            placeholder="search packages..."
            size="small"
            slotProps={{
                input: {
                    endAdornment: searchText ?
                        <InputAdornment position="end">
                            <IconButton aria-label="Clear search" onClick={() => onSearchChange("")} size="small">
                                <ClearIcon fontSize="small" />
                            </IconButton>
                        </InputAdornment>
                        : undefined,
                    startAdornment:
                            <InputAdornment position="start">
                                <SearchIcon fontSize="small" />
                            </InputAdornment>
                    ,
                },
            }}
            sx={{ minWidth: 200 }}
            value={searchText}
        />

        <Tooltip title="Export CSV">
            <IconButton aria-label="Export CSV" onClick={actions.onExportClick} size="small">
                <FileDownloadIcon fontSize="small" />
            </IconButton>
        </Tooltip>
    </Box>;
}
