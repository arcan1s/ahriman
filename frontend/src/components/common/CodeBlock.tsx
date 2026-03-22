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
import "components/common/syntaxLanguages";

import { Box, useTheme } from "@mui/material";
import CopyButton from "components/common/CopyButton";
import { useThemeMode } from "hooks/useThemeMode";
import React, { type RefObject } from "react";
import { Light as SyntaxHighlighter } from "react-syntax-highlighter";
import { githubGist, vs2015 } from "react-syntax-highlighter/dist/esm/styles/hljs";

interface CodeBlockProps {
    content: string;
    height?: number | string;
    language?: string;
    onScroll?: () => void;
    preRef?: RefObject<HTMLElement | null>;
}

export default function CodeBlock({
    content,
    height,
    language = "text",
    onScroll,
    preRef,
}: CodeBlockProps): React.JSX.Element {
    const { mode } = useThemeMode();
    const theme = useTheme();

    return <Box sx={{ position: "relative" }}>
        <Box
            onScroll={onScroll}
            ref={preRef}
            sx={{ overflow: "auto", height }}
        >
            <SyntaxHighlighter
                customStyle={{
                    borderRadius: `${theme.shape.borderRadius}px`,
                    fontSize: "0.8rem",
                    padding: theme.spacing(2),
                }}
                language={language}
                style={mode === "dark" ? vs2015 : githubGist}
                wrapLongLines
            >
                {content}
            </SyntaxHighlighter>
        </Box>
        {content && <Box sx={{ position: "absolute", right: 8, top: 8 }}>
            <CopyButton text={content} />
        </Box>}
    </Box>;
}
