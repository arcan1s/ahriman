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

export interface UsePackageActionsResult {
    handleReload: () => void;
    handleUpdate: () => Promise<void>;
    handleRefreshDatabase: () => Promise<void>;
    handleRemove: () => Promise<void>;
}

export function usePackageActions(
    selectionModel: string[],
    setSelectionModel: (model: string[]) => void,
): UsePackageActionsResult {
    const client = useClient();
    const { currentRepository } = useRepository();
    const { showSuccess, showError } = useNotification();
    const queryClient = useQueryClient();

    const invalidate = (repository: RepositoryId): void => {
        void queryClient.invalidateQueries({ queryKey: QueryKeys.packages(repository) });
        void queryClient.invalidateQueries({ queryKey: QueryKeys.status(repository) });
    };

    const performAction = async (
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
            setSelectionModel([]);
        } catch (exception) {
            showError("Action failed", `${errorMessage}: ${ApiError.errorDetail(exception)}`);
        }
    };

    const handleReload: () => void = () => {
        if (currentRepository !== null) {
            invalidate(currentRepository);
        }
    };

    const handleUpdate = (): Promise<void> => performAction(async (repository): Promise<string> => {
        if (selectionModel.length === 0) {
            await client.service.servicePackageUpdate(repository, { packages: [] });
            return "Repository update has been run";
        }
        await client.service.servicePackageAdd(repository, { packages: selectionModel });
        return `Run update for packages ${selectionModel.join(", ")}`;
    }, "Packages update failed");

    const handleRefreshDatabase = (): Promise<void> => performAction(async (repository): Promise<string> => {
        await client.service.servicePackageUpdate(repository, {
            packages: [],
            refresh: true,
            aur: false,
            local: false,
            manual: false,
        });
        return "Pacman database update has been requested";
    }, "Could not update pacman databases");

    const handleRemove = (): Promise<void> => {
        if (selectionModel.length === 0) {
            return Promise.resolve();
        }
        return performAction(async (repository): Promise<string> => {
            await client.service.servicePackageRemove(repository, selectionModel);
            return `Packages ${selectionModel.join(", ")} have been removed`;
        }, "Could not remove packages");
    };

    return {
        handleReload,
        handleUpdate,
        handleRefreshDatabase,
        handleRemove,
    };
}
