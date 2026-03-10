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
import { Box, Dialog, DialogContent, Grid, Typography } from "@mui/material";
import { skipToken, useQuery } from "@tanstack/react-query";
import PackageCountBarChart from "components/charts/PackageCountBarChart";
import StatusPieChart from "components/charts/StatusPieChart";
import DialogHeader from "components/common/DialogHeader";
import { QueryKeys } from "hooks/QueryKeys";
import { useClient } from "hooks/useClient";
import { useRepository } from "hooks/useRepository";
import type { InternalStatus } from "models/InternalStatus";
import type React from "react";
import { StatusHeaderStyles } from "theme/StatusColors";

interface DashboardDialogProps {
    open: boolean;
    onClose: () => void;
}

export default function DashboardDialog({ open, onClose }: DashboardDialogProps): React.JSX.Element {
    const client = useClient();
    const { currentRepository } = useRepository();

    const { data: status } = useQuery<InternalStatus>({
        queryKey: currentRepository ? QueryKeys.status(currentRepository) : ["status"],
        queryFn: currentRepository ? () => client.fetch.fetchServerStatus(currentRepository) : skipToken,
        enabled: open,
    });

    const headerStyle = status ? StatusHeaderStyles[status.status.status] : {};

    return <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
        <DialogHeader onClose={onClose} sx={headerStyle}>
            System health
        </DialogHeader>

        <DialogContent>
            {status &&
                <>
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                        <Grid size={{ xs: 6, md: 3 }}>
                            <Typography variant="body2" color="text.secondary" align="right">Repository name</Typography>
                        </Grid>
                        <Grid size={{ xs: 6, md: 3 }}>
                            <Typography variant="body2">{status.repository}</Typography>
                        </Grid>
                        <Grid size={{ xs: 6, md: 3 }}>
                            <Typography variant="body2" color="text.secondary" align="right">Repository architecture</Typography>
                        </Grid>
                        <Grid size={{ xs: 6, md: 3 }}>
                            <Typography variant="body2">{status.architecture}</Typography>
                        </Grid>
                    </Grid>

                    <Grid container spacing={2} sx={{ mt: 1 }}>
                        <Grid size={{ xs: 6, md: 3 }}>
                            <Typography variant="body2" color="text.secondary" align="right">Current status</Typography>
                        </Grid>
                        <Grid size={{ xs: 6, md: 3 }}>
                            <Typography variant="body2">{status.status.status}</Typography>
                        </Grid>
                        <Grid size={{ xs: 6, md: 3 }}>
                            <Typography variant="body2" color="text.secondary" align="right">Updated at</Typography>
                        </Grid>
                        <Grid size={{ xs: 6, md: 3 }}>
                            <Typography variant="body2">{new Date(status.status.timestamp * 1000).toISOStringShort()}</Typography>
                        </Grid>
                    </Grid>

                    <Grid container spacing={2} sx={{ mt: 2 }}>
                        <Grid size={{ xs: 12, md: 6 }}>
                            <Box sx={{ height: 300 }}>
                                <PackageCountBarChart stats={status.stats} />
                            </Box>
                        </Grid>
                        <Grid size={{ xs: 12, md: 6 }}>
                            <Box sx={{ height: 300, display: "flex", justifyContent: "center", alignItems: "center" }}>
                                <StatusPieChart counters={status.packages} />
                            </Box>
                        </Grid>
                    </Grid>
                </>
            }
        </DialogContent>
    </Dialog>;
}
