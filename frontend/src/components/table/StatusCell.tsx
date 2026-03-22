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
import PauseCircleIcon from "@mui/icons-material/PauseCircle";
import { Chip } from "@mui/material";
import type { BuildStatus } from "models/BuildStatus";
import type React from "react";
import { StatusColors } from "theme/StatusColors";

interface StatusCellProps {
    isHeld?: boolean;
    status: BuildStatus;
}

export default function StatusCell({ isHeld, status }: StatusCellProps): React.JSX.Element {
    return <Chip
        icon={isHeld ? <PauseCircleIcon /> : undefined}
        label={status}
        size="small"
        sx={{
            backgroundColor: StatusColors[status],
            color: "common.white",
            fontWeight: 500,
        }}
    />;
}
