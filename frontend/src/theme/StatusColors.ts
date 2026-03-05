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
import { amber, green, grey, orange, red } from "@mui/material/colors";
import type { BuildStatus } from "models/BuildStatus";

const base: Record<BuildStatus, string> = {
    unknown: grey[800],
    pending: amber[900],
    building: orange[900],
    failed: red[900],
    success: green[800],
};

const headerBase: Record<BuildStatus, string> = {
    unknown: grey[800],
    pending: amber[700],
    building: orange[600],
    failed: red[500],
    success: green[600],
};

export const StatusColors = base;

export const StatusHeaderStyles: Record<BuildStatus, { backgroundColor: string; color: string }> = Object.fromEntries(
    Object.entries(headerBase).map(([key, value]) => [key, { backgroundColor: value, color: "#fff" }]),
) as Record<BuildStatus, { backgroundColor: string; color: string }>;
