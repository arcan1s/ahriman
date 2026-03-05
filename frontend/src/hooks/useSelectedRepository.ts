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
import { useRepository } from "hooks/useRepository";
import type { RepositoryId } from "models/RepositoryId";
import { useState } from "react";

export interface SelectedRepositoryResult {
    selectedKey: string;
    setSelectedKey: (key: string) => void;
    selectedRepository: RepositoryId | null;
    reset: () => void;
}

export function useSelectedRepository(): SelectedRepositoryResult {
    const { repositories, current } = useRepository();
    const [selectedKey, setSelectedKey] = useState("");

    let selectedRepository: RepositoryId | null = current;
    if (selectedKey) {
        const repository = repositories.find(repository => repository.key === selectedKey);
        if (repository) {
            selectedRepository = repository;
        }
    }

    const reset: () => void = () => {
        setSelectedKey("");
    };

    return { selectedKey, setSelectedKey, selectedRepository, reset };
}
