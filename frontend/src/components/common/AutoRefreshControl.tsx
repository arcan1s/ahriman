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
import CheckIcon from "@mui/icons-material/Check";
import TimerIcon from "@mui/icons-material/Timer";
import TimerOffIcon from "@mui/icons-material/TimerOff";
import { IconButton, ListItemIcon, ListItemText, Menu, MenuItem, Tooltip } from "@mui/material";
import type { AutoRefreshInterval } from "models/AutoRefreshInterval";
import React, { useState } from "react";

interface AutoRefreshControlProps {
    currentInterval: number;
    intervals: AutoRefreshInterval[];
    onIntervalChange: (interval: number) => void;
}

export default function AutoRefreshControl({
    currentInterval,
    intervals,
    onIntervalChange,
}: AutoRefreshControlProps): React.JSX.Element | null {
    const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);

    if (intervals.length === 0) {
        return null;
    }

    const enabled = currentInterval > 0;

    return <>
        <Tooltip title="Auto-refresh">
            <IconButton
                aria-label="Auto-refresh"
                color={enabled ? "primary" : "default"}
                onClick={event => setAnchorEl(event.currentTarget)}
                size="small"
            >
                {enabled ? <TimerIcon fontSize="small" /> : <TimerOffIcon fontSize="small" />}
            </IconButton>
        </Tooltip>
        <Menu
            anchorEl={anchorEl}
            onClose={() => setAnchorEl(null)}
            open={Boolean(anchorEl)}
        >
            <MenuItem
                onClick={() => {
                    onIntervalChange(0);
                    setAnchorEl(null);
                }}
                selected={!enabled}
            >
                <ListItemIcon>
                    {!enabled && <CheckIcon fontSize="small" />}
                </ListItemIcon>
                <ListItemText>Off</ListItemText>
            </MenuItem>
            {intervals.map(interval =>
                <MenuItem
                    key={interval.interval}
                    onClick={() => {
                        onIntervalChange(interval.interval);
                        setAnchorEl(null);
                    }}
                    selected={enabled && interval.interval === currentInterval}
                >
                    <ListItemIcon>
                        {enabled && interval.interval === currentInterval && <CheckIcon fontSize="small" />}
                    </ListItemIcon>
                    <ListItemText>{interval.text}</ListItemText>
                </MenuItem>,
            )}
        </Menu>
    </>;
}
