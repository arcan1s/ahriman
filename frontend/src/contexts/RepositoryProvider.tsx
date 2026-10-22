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
import { navigate, packageHref, useLocationQuery } from "hooks/useLocationQuery";
import type { RepositoryId } from "models/RepositoryId";
import React, { type ReactNode, useCallback, useMemo, useState } from "react";

export function RepositoryProvider({ children }: { children: ReactNode }): React.JSX.Element {
    const [repositories, setRepositories] = useState<RepositoryId[]>([]);
    const repositoryKey = new URLSearchParams(useLocationQuery()).get("repository_id");

    const currentRepository = useMemo(() => {
        if (repositories.length === 0) {
            return null;
        }
        return repositories.find(repository => repository.key === repositoryKey) ?? repositories[0] ?? null;
    }, [repositories, repositoryKey]);

    const setCurrentRepository = useCallback((repository: RepositoryId) => {
        navigate(packageHref(repository.key, null));
    }, []);

    const value = useMemo(() => ({
        repositories, currentRepository, setRepositories, setCurrentRepository,
    }), [repositories, currentRepository, setCurrentRepository]);

    return <RepositoryContext.Provider value={value}>{children}</RepositoryContext.Provider>;
}
