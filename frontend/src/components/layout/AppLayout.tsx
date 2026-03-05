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
import { Box, Container } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import LoginDialog from "components/dialogs/LoginDialog";
import Footer from "components/layout/Footer";
import Navbar from "components/layout/Navbar";
import PackageTable from "components/table/PackageTable";
import { QueryKeys } from "hooks/QueryKeys";
import { useAuth } from "hooks/useAuth";
import { useClient } from "hooks/useClient";
import { useRepository } from "hooks/useRepository";
import type { InfoResponse } from "models/InfoResponse";
import React, { useEffect, useState } from "react";

export default function AppLayout(): React.JSX.Element {
    const client = useClient();
    const { setAuthState } = useAuth();
    const { setRepositories } = useRepository();
    const [loginOpen, setLoginOpen] = useState(false);

    const { data: info } = useQuery<InfoResponse>({
        queryKey: QueryKeys.info,
        queryFn: () => client.fetch.fetchServerInfo(),
        staleTime: Infinity,
    });

    // Sync info to contexts when loaded
    useEffect(() => {
        if (info) {
            setAuthState({ enabled: info.auth.enabled, username: info.auth.username ?? null });
            setRepositories(info.repositories);
        }
    }, [info, setAuthState, setRepositories]);

    return <Container maxWidth="xl">
        <Box sx={{ display: "flex", alignItems: "center", py: 1, gap: 1 }}>
            <a href="https://github.com/arcan1s/ahriman" title="logo">
                <img src="/static/logo.svg" width={30} height={30} alt="" />
            </a>
            <Box sx={{ flex: 1 }}>
                <Navbar />
            </Box>
        </Box>

        <PackageTable
            autoRefreshIntervals={info?.autorefresh_intervals ?? []}
        />

        <Footer
            version={info?.version ?? ""}
            docsEnabled={info?.docs_enabled ?? false}
            indexUrl={info?.index_url}
            onLoginClick={() => info?.auth.external ? window.location.assign("/api/v1/login") : setLoginOpen(true)}
        />

        <LoginDialog open={loginOpen} onClose={() => setLoginOpen(false)} />
    </Container>;
}
