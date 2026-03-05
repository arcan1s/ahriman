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
import { Grid, Link, Typography } from "@mui/material";
import type { Dependencies } from "models/Dependencies";
import type { Package } from "models/Package";
import React from "react";

interface PackageDetailsGridProps {
    pkg: Package;
    dependencies?: Dependencies;
}

export default function PackageDetailsGrid({ pkg, dependencies }: PackageDetailsGridProps): React.JSX.Element {
    const packagesList = Object.entries(pkg.packages)
        .map(([name, properties]) => `${name}${properties.description ? ` (${properties.description})` : ""}`);

    const groups = Object.values(pkg.packages)
        .flatMap(properties => properties.groups ?? []);

    const licenses = Object.values(pkg.packages)
        .flatMap(properties => properties.licenses ?? []);

    const upstreamUrls = Object.values(pkg.packages)
        .map(properties => properties.url)
        .filter((url): url is string => !!url)
        .unique();

    const aurUrl = pkg.remote.web_url;

    const pkgNames = Object.keys(pkg.packages);
    const pkgValues = Object.values(pkg.packages);
    const deps = pkgValues
        .flatMap(properties => (properties.depends ?? []).filter(dep => !pkgNames.includes(dep)))
        .unique();
    const makeDeps = pkgValues
        .flatMap(properties => (properties.make_depends ?? []).filter(dep => !pkgNames.includes(dep)))
        .map(dep => `${dep} (make)`)
        .unique();
    const optDeps = pkgValues
        .flatMap(properties => (properties.opt_depends ?? []).filter(dep => !pkgNames.includes(dep)))
        .map(dep => `${dep} (optional)`)
        .unique();
    const allDepends = [...deps, ...makeDeps, ...optDeps];

    const implicitDepends = dependencies
        ? Object.values(dependencies.paths).flat()
        : [];

    return <>
        <Grid container spacing={1} sx={{ mt: 1 }}>
            <Grid size={{ xs: 4, md: 1 }}><Typography variant="body2" color="text.secondary" align="right">packages</Typography></Grid>
            <Grid size={{ xs: 8, md: 5 }}><Typography variant="body2" sx={{ whiteSpace: "pre-line" }}>{packagesList.unique().join("\n")}</Typography></Grid>
            <Grid size={{ xs: 4, md: 1 }}><Typography variant="body2" color="text.secondary" align="right">version</Typography></Grid>
            <Grid size={{ xs: 8, md: 5 }}><Typography variant="body2">{pkg.version}</Typography></Grid>
        </Grid>

        <Grid container spacing={1} sx={{ mt: 0.5 }}>
            <Grid size={{ xs: 4, md: 1 }}><Typography variant="body2" color="text.secondary" align="right">packager</Typography></Grid>
            <Grid size={{ xs: 8, md: 5 }}><Typography variant="body2">{pkg.packager ?? ""}</Typography></Grid>
            <Grid size={{ xs: 4, md: 1 }} />
            <Grid size={{ xs: 8, md: 5 }} />
        </Grid>

        <Grid container spacing={1} sx={{ mt: 0.5 }}>
            <Grid size={{ xs: 4, md: 1 }}><Typography variant="body2" color="text.secondary" align="right">groups</Typography></Grid>
            <Grid size={{ xs: 8, md: 5 }}><Typography variant="body2" sx={{ whiteSpace: "pre-line" }}>{groups.unique().join("\n")}</Typography></Grid>
            <Grid size={{ xs: 4, md: 1 }}><Typography variant="body2" color="text.secondary" align="right">licenses</Typography></Grid>
            <Grid size={{ xs: 8, md: 5 }}><Typography variant="body2" sx={{ whiteSpace: "pre-line" }}>{licenses.unique().join("\n")}</Typography></Grid>
        </Grid>

        <Grid container spacing={1} sx={{ mt: 0.5 }}>
            <Grid size={{ xs: 4, md: 1 }}><Typography variant="body2" color="text.secondary" align="right">upstream</Typography></Grid>
            <Grid size={{ xs: 8, md: 5 }}>
                {upstreamUrls.map(url =>
                    <Link key={url} href={url} target="_blank" rel="noopener noreferrer" underline="hover" display="block" variant="body2">
                        {url}
                    </Link>,
                )}
            </Grid>
            <Grid size={{ xs: 4, md: 1 }}><Typography variant="body2" color="text.secondary" align="right">AUR</Typography></Grid>
            <Grid size={{ xs: 8, md: 5 }}>
                <Typography variant="body2">
                    {aurUrl &&
                        <Link href={aurUrl} target="_blank" rel="noopener noreferrer" underline="hover">AUR link</Link>
                    }
                </Typography>
            </Grid>
        </Grid>

        <Grid container spacing={1} sx={{ mt: 0.5 }}>
            <Grid size={{ xs: 4, md: 1 }}><Typography variant="body2" color="text.secondary" align="right">depends</Typography></Grid>
            <Grid size={{ xs: 8, md: 5 }}><Typography variant="body2" sx={{ whiteSpace: "pre-line" }}>{allDepends.join("\n")}</Typography></Grid>
            <Grid size={{ xs: 4, md: 1 }}><Typography variant="body2" color="text.secondary" align="right">implicitly depends</Typography></Grid>
            <Grid size={{ xs: 8, md: 5 }}><Typography variant="body2" sx={{ whiteSpace: "pre-line" }}>{implicitDepends.unique().join("\n")}</Typography></Grid>
        </Grid>
    </>;
}
