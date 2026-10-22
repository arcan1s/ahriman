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
import { useSyncExternalStore } from "react";

function subscribe(callback: () => void): () => void {
    window.addEventListener("popstate", callback);
    return () => window.removeEventListener("popstate", callback);
}

function getSnapshot(): string {
    return window.location.search;
}

export function useLocationQuery(): string {
    return useSyncExternalStore(subscribe, getSnapshot);
}

export function packageHref(repositoryKey: string, packageBase: string | null): string {
    const query = new URLSearchParams(window.location.search);
    query.set("repository_id", repositoryKey);
    if (packageBase) {
        query.set("package", packageBase);
    } else {
        query.delete("package");
    }
    return `${window.location.pathname}?${query}`;
}

export function navigate(href: string): void {
    if (href === `${window.location.pathname}${window.location.search}`) {
        return;
    }
    window.history.pushState(null, "", href);
    window.dispatchEvent(new PopStateEvent("popstate"));
}
