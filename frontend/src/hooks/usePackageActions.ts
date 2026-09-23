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
import { useQueryClient } from "@tanstack/react-query";
import { ApiError } from "api/client/ApiError";
import { QueryKeys } from "hooks/QueryKeys";
import { useClient } from "hooks/useClient";
import { useNotification } from "hooks/useNotification";
import { useRepository } from "hooks/useRepository";
import type { RepositoryId } from "models/RepositoryId";
import { useCallback } from "react";

export interface UsePackageActionsResult {
    handleRefreshDatabase: () => Promise<void>;
    handleReload: () => void;
    handleRemove: (packages: string[]) => Promise<void>;
    handleUpdate: (packages: string[]) => Promise<void>;
}

export function usePackageActions(): UsePackageActionsResult {
    const client = useClient();
    const { currentRepository } = useRepository();
    const { showSuccess, showError } = useNotification();
    const queryClient = useQueryClient();

    const invalidate = useCallback((repository: RepositoryId): void => {
        void queryClient.invalidateQueries({ queryKey: QueryKeys.packages(repository) });
        void queryClient.invalidateQueries({ queryKey: QueryKeys.status(repository) });
    }, [queryClient]);

    const performAction = useCallback(async (
        action: (repository: RepositoryId) => Promise<string>,
        errorMessage: string,
    ): Promise<void> => {
        if (!currentRepository) {
            return;
        }
        try {
            const successMessage = await action(currentRepository);
            showSuccess("Success", successMessage);
            invalidate(currentRepository);
        } catch (exception) {
            showError("Action failed", `${errorMessage}: ${ApiError.errorDetail(exception)}`);
        }
    }, [currentRepository, invalidate, showError, showSuccess]);

    const handleReload = (): void => {
        if (currentRepository !== null) {
            invalidate(currentRepository);
        }
    };

    const handleUpdate = useCallback((packages: string[]): Promise<void> => {
        return performAction(async (repository): Promise<string> => {
            if (packages.length === 0) {
                await client.service.servicePackageUpdate(repository, { packages: [] });
                return "Repository update has been run";
            }
            await client.service.servicePackageAdd(repository, { packages });
            return `Run update for packages ${packages.join(", ")}`;
        }, "Packages update failed");
    }, [client, performAction]);

    const handleRefreshDatabase = (): Promise<void> => performAction(async (repository): Promise<string> => {
        await client.service.servicePackageUpdate(repository, {
            aur: false,
            local: false,
            manual: false,
            packages: [],
            refresh: true,
        });
        return "Pacman database update has been requested";
    }, "Could not update pacman databases");

    const handleRemove = useCallback((packages: string[]): Promise<void> => {
        if (packages.length === 0) {
            return Promise.resolve();
        }
        return performAction(async (repository): Promise<string> => {
            await client.service.servicePackageRemove(repository, packages);
            return `Packages ${packages.join(", ")} have been removed`;
        }, "Could not remove packages");
    }, [client, performAction]);

    return {
        handleRefreshDatabase,
        handleReload,
        handleRemove,
        handleUpdate,
    };
}
