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
import DeleteIcon from "@mui/icons-material/Delete";
import PauseCircleIcon from "@mui/icons-material/PauseCircle";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import PlayCircleIcon from "@mui/icons-material/PlayCircle";
import { Button, Checkbox, DialogActions, FormControlLabel } from "@mui/material";
import AutoRefreshControl from "components/common/AutoRefreshControl";
import type { AutoRefreshInterval } from "models/AutoRefreshInterval";
import type React from "react";

interface PackageInfoActionsProps {
    autoRefreshInterval: number;
    autoRefreshIntervals: AutoRefreshInterval[];
    isAuthorized: boolean;
    isHeld: boolean;
    onAutoRefreshIntervalChange: (interval: number) => void;
    onHoldToggle: () => void;
    onRefreshDatabaseChange: (checked: boolean) => void;
    onRemove: () => void;
    onUpdate: () => void;
    refreshDatabase: boolean;
}

export default function PackageInfoActions({
    autoRefreshInterval,
    autoRefreshIntervals,
    isAuthorized,
    isHeld,
    onAutoRefreshIntervalChange,
    onHoldToggle,
    onRefreshDatabaseChange,
    onRemove,
    onUpdate,
    refreshDatabase,
}: PackageInfoActionsProps): React.JSX.Element {
    return <DialogActions sx={{ flexWrap: "wrap", gap: 1 }}>
        {isAuthorized &&
            <>
                <FormControlLabel
                    control={<Checkbox checked={refreshDatabase} onChange={(_, checked) => onRefreshDatabaseChange(checked)} size="small" />}
                    label="update pacman databases"
                />
                <Button color="warning" onClick={onHoldToggle} size="small" startIcon={isHeld ? <PlayCircleIcon /> : <PauseCircleIcon />} variant="outlined">
                    {isHeld ? "unhold" : "hold"}
                </Button>
                <Button color="success" onClick={onUpdate} size="small" startIcon={<PlayArrowIcon />} variant="contained">
                    update
                </Button>
                <Button color="error" onClick={onRemove} size="small" startIcon={<DeleteIcon />} variant="contained">
                    remove
                </Button>
            </>
        }
        <AutoRefreshControl
            currentInterval={autoRefreshInterval}
            intervals={autoRefreshIntervals}
            onIntervalChange={onAutoRefreshIntervalChange}
        />
    </DialogActions>;
}
