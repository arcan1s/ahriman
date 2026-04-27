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
import ListIcon from "@mui/icons-material/List";
import { Box, Button, Menu, MenuItem, Typography } from "@mui/material";
import { keepPreviousData, skipToken, useQuery } from "@tanstack/react-query";
import CodeBlock from "components/common/CodeBlock";
import { QueryKeys } from "hooks/QueryKeys";
import { useAutoScroll } from "hooks/useAutoScroll";
import { useBuildLogStream } from "hooks/useBuildLogStream";
import { useClient } from "hooks/useClient";
import type { LogRecord } from "models/LogRecord";
import type { RepositoryId } from "models/RepositoryId";
import React, { useEffect, useMemo, useState } from "react";

interface Logs {
    created: number;
    logs: string;
    processId: string;
    version: string;
}

interface BuildLogsTabProps {
    packageBase: string;
    repository: RepositoryId;
}

function convertLogs(records: LogRecord[], filter?: (record: LogRecord) => boolean): string {
    const filtered = filter ? records.filter(filter) : records;
    return filtered
        .map(record => `[${new Date(record.created * 1000).toISOString()}] ${record.message}`)
        .join("\n");
}

export default function BuildLogsTab({
    packageBase,
    repository,
}: BuildLogsTabProps): React.JSX.Element {
    const client = useClient();
    useBuildLogStream(packageBase, repository);
    const [selectedVersionKey, setSelectedVersionKey] = useState<string | null>(null);
    const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);

    const { data: allLogs } = useQuery<LogRecord[]>({
        enabled: !!packageBase,
        queryFn: () => client.fetch.fetchPackageLogs(packageBase, repository),
        queryKey: QueryKeys.logs(packageBase, repository),
    });

    // Build version selectors from all logs
    const versions = useMemo<Logs[]>(() => {
        if (!allLogs || allLogs.length === 0) {
            return [];
        }

        const grouped: Record<string, LogRecord & { minCreated: number }> = {};
        for (const record of allLogs) {
            const key = `${record.version}-${record.process_id}`;
            const existing = grouped[key];
            if (!existing) {
                grouped[key] = { ...record, minCreated: record.created };
            } else {
                existing.minCreated = Math.min(existing.minCreated, record.created);
            }
        }

        return Object.values(grouped)
            .sort((left, right) => right.minCreated - left.minCreated)
            .map(record => ({
                created: record.minCreated,
                logs: convertLogs(
                    allLogs,
                    right => record.version === right.version && record.process_id === right.process_id,
                ),
                processId: record.process_id,
                version: record.version,
            }));
    }, [allLogs]);

    // Compute active index from selected version key, defaulting to newest (index 0)
    const activeIndex = useMemo(() => {
        if (selectedVersionKey) {
            const index = versions.findIndex(record => `${record.version}-${record.processId}` === selectedVersionKey);
            if (index >= 0) {
                return index;
            }
        }
        return 0;
    }, [versions, selectedVersionKey]);

    const activeVersion = versions[activeIndex];
    const activeVersionKey = activeVersion ? `${activeVersion.version}-${activeVersion.processId}` : null;

    // Refresh active version logs
    const { data: versionLogs } = useQuery<LogRecord[]>({
        placeholderData: keepPreviousData,
        queryFn: activeVersion
            ? () => client.fetch.fetchPackageLogs(
                packageBase, repository, activeVersion.version, activeVersion.processId,
            )
            : skipToken,
        queryKey: QueryKeys.logsVersion(packageBase, repository, activeVersion?.version ?? "", activeVersion?.processId ?? ""),
    });

    // Derive displayed logs: prefer fresh polled data when available
    const displayedLogs = useMemo(() => {
        if (versionLogs && versionLogs.length > 0) {
            return convertLogs(versionLogs);
        }
        return activeVersion?.logs ?? "";
    }, [versionLogs, activeVersion]);

    const { preRef, handleScroll, scrollToBottom, resetScroll } = useAutoScroll();

    // Reset scroll tracking when active version changes
    useEffect(() => {
        resetScroll();
    }, [activeVersionKey, resetScroll]);

    // Scroll to bottom on new logs
    useEffect(() => {
        scrollToBottom();
    }, [displayedLogs, scrollToBottom]);

    return <Box sx={{ display: "flex", gap: 1, mt: 1 }}>
        <Box>
            <Button
                aria-label="Select version"
                onClick={event => setAnchorEl(event.currentTarget)}
                size="small"
                startIcon={<ListIcon />}
            />
            <Menu
                anchorEl={anchorEl}
                onClose={() => setAnchorEl(null)}
                open={Boolean(anchorEl)}
            >
                {versions.map((logs, index) =>
                    <MenuItem
                        key={`${logs.version}-${logs.processId}`}
                        onClick={() => {
                            setSelectedVersionKey(`${logs.version}-${logs.processId}`);
                            setAnchorEl(null);
                            resetScroll();
                        }}
                        selected={index === activeIndex}
                    >
                        <Typography variant="body2">{new Date(logs.created * 1000).toISOStringShort()}</Typography>
                    </MenuItem>,
                )}
                {versions.length === 0 &&
                    <MenuItem disabled>No logs available</MenuItem>
                }
            </Menu>
        </Box>

        <Box sx={{ flex: 1 }}>
            <CodeBlock
                content={displayedLogs}
                height={400}
                onScroll={handleScroll}
                preRef={preRef}
            />
        </Box>
    </Box>;
}
