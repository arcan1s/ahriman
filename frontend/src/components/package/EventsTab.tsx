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
import { Box } from "@mui/material";
import { DataGrid, type GridColDef } from "@mui/x-data-grid";
import { useQuery } from "@tanstack/react-query";
import EventDurationLineChart from "components/charts/EventDurationLineChart";
import { QueryKeys } from "hooks/QueryKeys";
import { useClient } from "hooks/useClient";
import type { Event } from "models/Event";
import type { RepositoryId } from "models/RepositoryId";
import type React from "react";
import { useMemo } from "react";

interface EventsTabProps {
    packageBase: string;
    repository: RepositoryId;
}

interface EventRow {
    id: number;
    timestamp: string;
    event: string;
    message: string;
}

const columns: GridColDef<EventRow>[] = [
    { field: "timestamp", headerName: "date", width: 180, align: "right", headerAlign: "right" },
    { field: "event", headerName: "event", flex: 1 },
    { field: "message", headerName: "description", flex: 2 },
];

export default function EventsTab({ packageBase, repository }: EventsTabProps): React.JSX.Element {
    const client = useClient();

    const { data: events = [] } = useQuery<Event[]>({
        queryKey: QueryKeys.events(repository, packageBase),
        queryFn: () => client.fetch.fetchPackageEvents(repository, packageBase, 30),
        enabled: !!packageBase,
    });

    const rows = useMemo<EventRow[]>(() => events.map((event, index) => ({
        id: index,
        timestamp: new Date(event.created * 1000).toISOStringShort(),
        event: event.event,
        message: event.message ?? "",
    })), [events]);

    return <Box sx={{ mt: 1 }}>
        <EventDurationLineChart events={events} />
        <DataGrid
            rows={rows}
            columns={columns}
            density="compact"
            disableColumnSorting
            disableRowSelectionOnClick
            pageSizeOptions={[10, 25]}
            sx={{ height: 400, mt: 1 }}
        />
    </Box>;
}
