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
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import { Button, Checkbox, DialogActions, FormControlLabel } from "@mui/material";
import AutoRefreshControl from "components/common/AutoRefreshControl";
import type { AutoRefreshInterval } from "models/AutoRefreshInterval";
import type React from "react";

interface PackageInfoActionsProps {
    isAuthorized: boolean;
    refreshDatabase: boolean;
    onRefreshDatabaseChange: (checked: boolean) => void;
    onUpdate: () => void;
    onRemove: () => void;
    autoRefreshIntervals: AutoRefreshInterval[];
    autoRefreshInterval: number;
    onAutoRefreshIntervalChange: (interval: number) => void;
}

export default function PackageInfoActions({
    isAuthorized,
    refreshDatabase,
    onRefreshDatabaseChange,
    onUpdate,
    onRemove,
    autoRefreshIntervals,
    autoRefreshInterval,
    onAutoRefreshIntervalChange,
}: PackageInfoActionsProps): React.JSX.Element {
    return <DialogActions sx={{ flexWrap: "wrap", gap: 1 }}>
        {isAuthorized &&
            <>
                <FormControlLabel
                    control={<Checkbox checked={refreshDatabase} onChange={(_, checked) => onRefreshDatabaseChange(checked)} size="small" />}
                    label="update pacman databases"
                />
                <Button onClick={onUpdate} variant="contained" color="success" startIcon={<PlayArrowIcon />} size="small">
                    update
                </Button>
                <Button onClick={onRemove} variant="contained" color="error" startIcon={<DeleteIcon />} size="small">
                    remove
                </Button>
            </>
        }
        <AutoRefreshControl
            intervals={autoRefreshIntervals}
            currentInterval={autoRefreshInterval}
            onIntervalChange={onAutoRefreshIntervalChange}
        />
    </DialogActions>;
}
