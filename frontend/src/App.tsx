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
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import AppLayout from "components/layout/AppLayout";
import { AuthProvider } from "contexts/AuthProvider";
import { ClientProvider } from "contexts/ClientProvider";
import { NotificationProvider } from "contexts/NotificationProvider";
import { RepositoryProvider } from "contexts/RepositoryProvider";
import { ThemeProvider } from "contexts/ThemeProvider";
import type React from "react";

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: 1,
            staleTime: 30_000,
        },
    },
});

export default function App(): React.JSX.Element {
    return <QueryClientProvider client={queryClient}>
        <ThemeProvider>
            <NotificationProvider>
                <ClientProvider>
                    <AuthProvider>
                        <RepositoryProvider>
                            <AppLayout />
                        </RepositoryProvider>
                    </AuthProvider>
                </ClientProvider>
            </NotificationProvider>
        </ThemeProvider>
    </QueryClientProvider>;
}
