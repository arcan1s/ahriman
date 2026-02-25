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
import type { Event } from "models/Event";
import type React from "react";
import { Line } from "react-chartjs-2";

interface EventDurationLineChartProps {
    events: Event[];
}

export default function EventDurationLineChart({ events }: EventDurationLineChartProps): React.JSX.Element {
    const updateEvents = events.filter(event => event.event === "package-updated");
    const data = {
        labels: updateEvents.map(event => new Date(event.created * 1000).toISOStringShort()),
        datasets: [
            {
                label: "update duration, s",
                data: updateEvents.map(event => event.data?.took ?? 0),
                cubicInterpolationMode: "monotone" as const,
                tension: 0.4,
            },
        ],
    };

    return <Line data={data} options={{ responsive: true }} />;
}
