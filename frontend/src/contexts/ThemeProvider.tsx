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
import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider as MuiThemeProvider } from "@mui/material/styles";
import { defaults as chartDefaults } from "chart.js";
import { ThemeContext } from "contexts/ThemeContext";
import { useLocalStorage } from "hooks/useLocalStorage";
import React, { useCallback, useEffect, useMemo } from "react";
import { createAppTheme } from "theme/Theme";

function systemPreference(): "light" | "dark" {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function ThemeProvider({ children }: { children: React.ReactNode }): React.JSX.Element {
    const [mode, setMode] = useLocalStorage<"light" | "dark">("theme-mode", systemPreference());

    const toggleTheme = useCallback(() => {
        setMode(prev => prev === "light" ? "dark" : "light");
    }, [setMode]);

    const theme = useMemo(() => createAppTheme(mode), [mode]);

    useEffect(() => {
        chartDefaults.color = mode === "dark" ? "rgba(255,255,255,0.7)" : "rgba(0,0,0,0.7)";
        chartDefaults.borderColor = mode === "dark" ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)";
    }, [mode]);

    const value = useMemo(() => ({ mode, toggleTheme }), [mode, toggleTheme]);

    return <ThemeContext.Provider value={value}>
        <MuiThemeProvider theme={theme}>
            <CssBaseline />
            {children}
        </MuiThemeProvider>
    </ThemeContext.Provider>;
}
