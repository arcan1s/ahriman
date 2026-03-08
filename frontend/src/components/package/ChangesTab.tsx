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
import { useQuery } from "@tanstack/react-query";
import CopyButton from "components/common/CopyButton";
import { QueryKeys } from "hooks/QueryKeys";
import { useClient } from "hooks/useClient";
import { useThemeMode } from "hooks/useThemeMode";
import type { Changes } from "models/Changes";
import type { RepositoryId } from "models/RepositoryId";
import React from "react";
import { Light as SyntaxHighlighter } from "react-syntax-highlighter";
import diff from "react-syntax-highlighter/dist/esm/languages/hljs/diff";
import { githubGist, vs2015 } from "react-syntax-highlighter/dist/esm/styles/hljs";

SyntaxHighlighter.registerLanguage("diff", diff);

interface ChangesTabProps {
    packageBase: string;
    repository: RepositoryId;
}

export default function ChangesTab({ packageBase, repository }: ChangesTabProps): React.JSX.Element {
    const client = useClient();
    const { mode } = useThemeMode();

    const { data } = useQuery<Changes>({
        queryKey: QueryKeys.changes(packageBase, repository),
        queryFn: () => client.fetch.fetchPackageChanges(packageBase, repository),
        enabled: !!packageBase,
    });

    const changesText = data?.changes ?? "";

    return <Box sx={{ position: "relative", mt: 1 }}>
        <SyntaxHighlighter
            language="diff"
            style={mode === "dark" ? vs2015 : githubGist}
            customStyle={{
                padding: "16px",
                borderRadius: "4px",
                overflow: "auto",
                height: 400,
                fontSize: "0.8rem",
                fontFamily: "monospace",
                margin: 0,
            }}
        >
            {changesText}
        </SyntaxHighlighter>
        <Box sx={{ position: "absolute", top: 8, right: 8 }}>
            <CopyButton getText={() => changesText} />
        </Box>
    </Box>;
}
