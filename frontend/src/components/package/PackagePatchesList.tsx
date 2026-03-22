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
import { Box, IconButton, TextField, Typography } from "@mui/material";
import type { Patch } from "models/Patch";
import type React from "react";

interface PackagePatchesListProps {
    editable: boolean;
    onDelete: (key: string) => void;
    patches: Patch[];
}

export default function PackagePatchesList({
    editable,
    onDelete,
    patches,
}: PackagePatchesListProps): React.JSX.Element | null {
    if (patches.length === 0) {
        return null;
    }

    return <Box sx={{ mt: 2 }}>
        <Typography gutterBottom variant="h6">Environment variables</Typography>
        {patches.map(patch =>
            <Box key={patch.key} sx={{ alignItems: "center", display: "flex", gap: 1, mb: 0.5 }}>
                <TextField
                    disabled
                    size="small"
                    sx={{ flex: 1 }}
                    value={patch.key}
                />
                <Box>=</Box>
                <TextField
                    disabled
                    value={JSON.stringify(patch.value)}
                    size="small"
                    sx={{ flex: 1 }}
                />
                {editable &&
                    <IconButton aria-label="Remove patch" color="error" onClick={() => onDelete(patch.key)} size="small">
                        <DeleteIcon fontSize="small" />
                    </IconButton>
                }
            </Box>,
        )}
    </Box>;
}
