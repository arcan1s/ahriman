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
import type { BuildStatus } from "models/BuildStatus";
import type { Counters } from "models/Counters";
import type React from "react";
import { Pie } from "react-chartjs-2";
import { StatusColors } from "theme/StatusColors";

interface StatusPieChartProps {
    counters: Counters;
}

export default function StatusPieChart({ counters }: StatusPieChartProps): React.JSX.Element {
    const labels = ["unknown", "pending", "building", "failed", "success"] as BuildStatus[];
    const data = {
        datasets: [
            {
                backgroundColor: labels.map(label => StatusColors[label]),
                data: labels.map(label => counters[label]),
                label: "packages in status",
            },
        ],
        labels: labels,
    };

    return <Pie data={data} options={{ responsive: true }} />;
}
