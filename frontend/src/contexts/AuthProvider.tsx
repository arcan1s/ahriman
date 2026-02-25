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
import { ApiError } from "api/client/ApiError";
import { AuthContext } from "contexts/AuthContext";
import { useClient } from "hooks/useClient";
import { useNotification } from "hooks/useNotification";
import React, { type ReactNode, useCallback, useMemo, useState } from "react";

export function AuthProvider({ children }: { children: ReactNode }): React.JSX.Element {
    const client = useClient();
    const [authState, setAuthState] = useState({ enabled: true, username: null as string | null });
    const { showError } = useNotification();

    const login = useCallback(async (username: string, password: string) => {
        await client.login({ username, password });
        setAuthState(prev => ({ ...prev, username }));
    }, [client]);

    const logout = useCallback(async () => {
        try {
            await client.logout();
            setAuthState(prev => ({ ...prev, username: null }));
        } catch (exception) {
            const detail = ApiError.errorDetail(exception);
            showError("Login error", `Could not log out: ${detail}`);
        }
    }, [client, showError]);

    const isAuthorized = useMemo(() =>
        !authState.enabled || authState.username !== null, [authState.enabled, authState.username],
    );

    const value = useMemo(() => ({
        ...authState, isAuthorized, setAuthState, login, logout,
    }), [authState, isAuthorized, login, logout]);

    return <AuthContext.Provider value={value}>
        {children}
    </AuthContext.Provider>;
}
