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
import { useQueryClient } from "@tanstack/react-query";
import { buildEventStreamUrl } from "hooks/useEventStream";
import { useNotification } from "hooks/useNotification";
import type { LogRecord } from "models/LogRecord";
import type { RepositoryId } from "models/RepositoryId";
import { useEffect } from "react";

interface BuildLogEvent {
    created: number;
    message: string;
    process_id: string;
    version: string;
}

function appendLogRecord(existing: LogRecord[] | undefined, record: LogRecord): LogRecord[] {
    return [...existing ?? [], record];
}

function invalidateLogs(queryClient: QueryClient, repository: RepositoryId, packageBase: string): void {
    void queryClient.invalidateQueries({ queryKey: ["logs", repository.key, packageBase] });
}

export function useBuildLogStream(packageBase: string, repository: RepositoryId): void {
    const queryClient = useQueryClient();
    const { showError } = useNotification();

    useEffect(() => {
        const source = new EventSource(buildEventStreamUrl(repository, ["build-log"], packageBase));
        let needsRefresh = false;

        source.addEventListener("error", () => {
            needsRefresh = true;
        });

        source.addEventListener("open", () => {
            if (needsRefresh) {
                invalidateLogs(queryClient, repository, packageBase);
                needsRefresh = false;
            }
        });

        source.addEventListener("build-log", (event: MessageEvent<string>) => {
            let data: BuildLogEvent;
            try {
                data = JSON.parse(event.data) as BuildLogEvent;
            } catch {
                showError("Live updates failed", "Could not parse build log event; refreshing logs.");
                invalidateLogs(queryClient, repository, packageBase);
                return;
            }

            const record: LogRecord = {
                created: data.created,
                message: data.message,
                process_id: data.process_id,
                version: data.version,
            };

            // Append to the all-logs cache
            queryClient.setQueryData<LogRecord[]>(
                ["logs", repository.key, packageBase],
                existing => appendLogRecord(existing, record),
            );

            // Append to the version-specific cache
            queryClient.setQueryData<LogRecord[]>(
                ["logs", repository.key, packageBase, record.version, record.process_id],
                existing => appendLogRecord(existing, record),
            );
        });

        return () => {
            source.close();
        };
    }, [queryClient, packageBase, repository, showError]);
}
