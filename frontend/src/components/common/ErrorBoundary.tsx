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
import { Box, Button, Typography } from "@mui/material";
import type React from "react";
import type { FallbackProps } from "react-error-boundary";

interface ErrorDetails {
    message: string;
    stack: string | undefined;
}

export default function ErrorFallback({ error }: FallbackProps): React.JSX.Element {

    const details: ErrorDetails = error instanceof Error
        ? { message: error.message, stack: error.stack }
        : { message: String(error), stack: undefined };

    return <Box role="alert" sx={{ color: "text.primary", minHeight: "100vh", p: 6 }}>
        <Typography sx={{ fontWeight: 700 }} variant="h4">
            Something went wrong
        </Typography>

        <Typography color="error" sx={{ fontFamily: "monospace", mt: 2 }}>
            {details.message}
        </Typography>

        {details.stack && <Typography
            component="pre"
            sx={{ color: "text.secondary", fontFamily: "monospace", fontSize: "0.75rem", mt: 3, whiteSpace: "pre-wrap", wordBreak: "break-word" }}
        >
            {details.stack}
        </Typography>}

        <Box sx={{ display: "flex", gap: 2, mt: 4 }}>
            <Button onClick={() => window.location.reload()} variant="outlined">Reload page</Button>
        </Box>
    </Box>;
}
