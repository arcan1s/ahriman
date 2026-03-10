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
import { RepositoryContext } from "contexts/RepositoryContext";
import type { RepositoryId } from "models/RepositoryId";
import React, { type ReactNode, useCallback, useMemo, useState, useSyncExternalStore } from "react";

function subscribeToHash(callback: () => void): () => void {
    window.addEventListener("hashchange", callback);
    return () => window.removeEventListener("hashchange", callback);
}

function getHashSnapshot(): string {
    return window.location.hash.replace("#", "");
}

export function RepositoryProvider({ children }: { children: ReactNode }): React.JSX.Element {
    const [repositories, setRepositories] = useState<RepositoryId[]>([]);
    const hash = useSyncExternalStore(subscribeToHash, getHashSnapshot);

    const currentRepository = useMemo(() => {
        if (repositories.length === 0) {
            return null;
        }
        return repositories.find(repository => repository.key === hash) ?? repositories[0] ?? null;
    }, [repositories, hash]);

    const setCurrentRepository = useCallback((repository: RepositoryId) => {
        window.location.hash = repository.key;
    }, []);

    const value = useMemo(() => ({
        repositories, currentRepository, setRepositories, setCurrentRepository,
    }), [repositories, currentRepository, setCurrentRepository]);

    return <RepositoryContext.Provider value={value}>{children}</RepositoryContext.Provider>;
}
