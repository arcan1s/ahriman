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
import { Box } from "@mui/material";
import CopyButton from "components/common/CopyButton";
import React, { type RefObject } from "react";

interface CodeBlockProps {
    preRef?: RefObject<HTMLElement | null>;
    getText: () => string;
    height?: number | string;
    onScroll?: () => void;
    wordBreak?: boolean;
}

export default function CodeBlock({
    preRef,
    getText,
    height,
    onScroll,
    wordBreak,
}: CodeBlockProps): React.JSX.Element {
    return <Box sx={{ position: "relative" }}>
        <Box
            ref={preRef}
            component="pre"
            onScroll={onScroll}
            sx={{
                backgroundColor: "action.hover",
                p: 2,
                borderRadius: 1,
                overflow: "auto",
                height,
                fontSize: "0.8rem",
                fontFamily: "monospace",
                ...wordBreak ? { whiteSpace: "pre-wrap", wordBreak: "break-all" } : {},
            }}
        >
            <code>
                {getText()}
            </code>
        </Box>
        <Box sx={{ position: "absolute", top: 8, right: 8 }}>
            <CopyButton getText={getText} />
        </Box>
    </Box>;
}
