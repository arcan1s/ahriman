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
import type { QueryClient } from "@tanstack/react-query";
import type { RepositoryId } from "models/RepositoryId";
import { useEffect } from "react";

const GLOBAL_EVENT_TYPES = [
    "package-held",
    "package-outdated",
    "package-removed",
    "package-status-changed",
    "package-update-failed",
    "package-updated",
    "service-status-changed",
] as const;

function invalidateForEvent(
    queryClient: QueryClient,
    repositoryKey: string,
    eventType: string,
    objectId?: string,
): void {
    switch (eventType) {
        case "package-status-changed":
        case "package-updated":
        case "package-removed":
        case "package-held":
            void queryClient.invalidateQueries({ queryKey: ["packages", repositoryKey] });
            void queryClient.invalidateQueries({ queryKey: ["status", repositoryKey] });
            if (objectId) {
                void queryClient.invalidateQueries({ queryKey: ["packages", repositoryKey, objectId] });
                void queryClient.invalidateQueries({ queryKey: ["events", repositoryKey, objectId] });
            }
            break;
        case "service-status-changed":
            void queryClient.invalidateQueries({ queryKey: ["status", repositoryKey] });
            break;
        case "package-outdated":
        case "package-update-failed":
            void queryClient.invalidateQueries({ queryKey: ["packages", repositoryKey] });
            if (objectId) {
                void queryClient.invalidateQueries({ queryKey: ["packages", repositoryKey, objectId] });
            }
            break;
    }
}

export function buildEventStreamUrl(
    repository: RepositoryId,
    events?: readonly string[],
    objectId?: string,
): string {
    const params = new URLSearchParams(repository.toQuery());
    if (events) {
        for (const event of events) {
            params.append("event", event);
        }
    }
    if (objectId) {
        params.set("object_id", objectId);
    }
    return `/api/v1/events/stream?${params.toString()}`;
}

export function useEventStream(queryClient: QueryClient, repository: RepositoryId | null): void {
    useEffect(() => {
        if (!repository) {
            return;
        }

        const source = new EventSource(buildEventStreamUrl(repository, GLOBAL_EVENT_TYPES));

        for (const eventType of GLOBAL_EVENT_TYPES) {
            source.addEventListener(eventType, (event: MessageEvent<string>) => {
                const data = JSON.parse(event.data) as { object_id?: string };
                invalidateForEvent(queryClient, repository.key, eventType, data.object_id ?? undefined);
            });
        }

        return () => {
            source.close();
        };
    }, [queryClient, repository]);
}
