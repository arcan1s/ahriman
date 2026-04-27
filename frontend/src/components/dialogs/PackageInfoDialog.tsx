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
import { Box, Dialog, DialogContent, Tab, Tabs } from "@mui/material";
import { skipToken, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError } from "api/client/ApiError";
import DialogHeader from "components/common/DialogHeader";
import ArtifactsTab from "components/package/ArtifactsTab";
import BuildLogsTab from "components/package/BuildLogsTab";
import ChangesTab from "components/package/ChangesTab";
import EventsTab from "components/package/EventsTab";
import PackageDetailsGrid from "components/package/PackageDetailsGrid";
import PackageInfoActions from "components/package/PackageInfoActions";
import PackagePatchesList from "components/package/PackagePatchesList";
import PkgbuildTab from "components/package/PkgbuildTab";
import { type TabKey, tabs } from "components/package/TabKey";
import { QueryKeys } from "hooks/QueryKeys";
import { useAuth } from "hooks/useAuth";
import { useClient } from "hooks/useClient";
import { useNotification } from "hooks/useNotification";
import { useRepository } from "hooks/useRepository";
import type { Dependencies } from "models/Dependencies";
import type { PackageStatus } from "models/PackageStatus";
import type { Patch } from "models/Patch";
import React, { useState } from "react";
import { StatusHeaderStyles } from "theme/StatusColors";

interface PackageInfoDialogProps {
    onClose: () => void;
    open: boolean;
    packageBase: string | null;
}

export default function PackageInfoDialog({
    onClose,
    open,
    packageBase,
}: PackageInfoDialogProps): React.JSX.Element {
    const client = useClient();
    const { currentRepository } = useRepository();
    const { isAuthorized } = useAuth();
    const { showSuccess, showError } = useNotification();
    const queryClient = useQueryClient();

    const [localPackageBase, setLocalPackageBase] = useState(packageBase);
    if (packageBase !== null && packageBase !== localPackageBase) {
        setLocalPackageBase(packageBase);
    }

    const [activeTab, setActiveTab] = useState<TabKey>("logs");
    const [refreshDatabase, setRefreshDatabase] = useState(true);

    const handleClose = (): void => {
        setActiveTab("logs");
        setRefreshDatabase(true);
        onClose();
    };

    const { data: packageData } = useQuery<PackageStatus[]>({
        enabled: open,
        queryFn: localPackageBase && currentRepository ?
            () => client.fetch.fetchPackage(localPackageBase, currentRepository) : skipToken,
        queryKey: localPackageBase && currentRepository ? QueryKeys.package(localPackageBase, currentRepository) : ["packages"],
    });

    const { data: dependencies } = useQuery<Dependencies>({
        enabled: open,
        queryFn: localPackageBase && currentRepository ?
            () => client.fetch.fetchPackageDependencies(localPackageBase, currentRepository) : skipToken,
        queryKey: localPackageBase && currentRepository ? QueryKeys.dependencies(localPackageBase, currentRepository) : ["dependencies"],
    });

    const { data: patches = [] } = useQuery<Patch[]>({
        enabled: open,
        queryFn: localPackageBase ? () => client.fetch.fetchPackagePatches(localPackageBase) : skipToken,
        queryKey: localPackageBase ? QueryKeys.patches(localPackageBase) : ["patches"],
    });

    const description = packageData?.[0];
    const pkg = description?.package;
    const status = description?.status;
    const headerStyle = status ? StatusHeaderStyles[status.status] : {};

    const handleUpdate = async (): Promise<void> => {
        if (!localPackageBase || !currentRepository) {
            return;
        }
        try {
            await client.service.servicePackageAdd(
                currentRepository, { packages: [localPackageBase], refresh: refreshDatabase });
            showSuccess("Success", `Run update for packages ${localPackageBase}`);
        } catch (exception) {
            showError("Action failed", `Package update failed: ${ApiError.errorDetail(exception)}`);
        }
    };

    const handleRemove = async (): Promise<void> => {
        if (!localPackageBase || !currentRepository) {
            return;
        }
        try {
            await client.service.servicePackageRemove(currentRepository, [localPackageBase]);
            showSuccess("Success", `Packages ${localPackageBase} have been removed`);
            onClose();
        } catch (exception) {
            showError("Action failed", `Could not remove package: ${ApiError.errorDetail(exception)}`);
        }
    };

    const handleHoldToggle = async (): Promise<void> => {
        if (!localPackageBase || !currentRepository) {
            return;
        }
        try {
            const newHeldStatus = !(status?.is_held ?? false);
            await client.service.servicePackageHold(localPackageBase, currentRepository, newHeldStatus);
            void queryClient.invalidateQueries({ queryKey: QueryKeys.package(localPackageBase, currentRepository) });
        } catch (exception) {
            showError("Action failed", `Could not update hold status: ${ApiError.errorDetail(exception)}`);
        }
    };

    const handleDeletePatch = async (key: string): Promise<void> => {
        if (!localPackageBase) {
            return;
        }
        try {
            await client.service.servicePackagePatchRemove(localPackageBase, key);
            void queryClient.invalidateQueries({ queryKey: QueryKeys.patches(localPackageBase) });
        } catch (exception) {
            showError("Action failed", `Could not delete variable: ${ApiError.errorDetail(exception)}`);
        }
    };

    return <Dialog fullWidth maxWidth="lg" onClose={handleClose} open={open}>
        <DialogHeader onClose={handleClose} sx={headerStyle}>
            {pkg && status
                ? `${pkg.base} ${status.status} at ${new Date(status.timestamp * 1000).toISOStringShort()}`
                : localPackageBase ?? ""}
        </DialogHeader>

        <DialogContent>
            {pkg &&
                <>
                    <PackageDetailsGrid dependencies={dependencies} pkg={pkg} />
                    <PackagePatchesList
                        editable={isAuthorized}
                        onDelete={key => void handleDeletePatch(key)}
                        patches={patches}
                    />

                    <Box sx={{ borderBottom: 1, borderColor: "divider", mt: 2 }}>
                        <Tabs onChange={(_, tab: TabKey) => setActiveTab(tab)} value={activeTab}>
                            {tabs.map(({ key, label }) => <Tab key={key} label={label} value={key} />)}
                        </Tabs>
                    </Box>

                    {activeTab === "logs" && localPackageBase && currentRepository &&
                        <BuildLogsTab
                            packageBase={localPackageBase}
                            repository={currentRepository}
                        />
                    }
                    {activeTab === "changes" && localPackageBase && currentRepository &&
                        <ChangesTab packageBase={localPackageBase} repository={currentRepository} />
                    }
                    {activeTab === "pkgbuild" && localPackageBase && currentRepository &&
                        <PkgbuildTab packageBase={localPackageBase} repository={currentRepository} />
                    }
                    {activeTab === "events" && localPackageBase && currentRepository &&
                        <EventsTab packageBase={localPackageBase} repository={currentRepository} />
                    }
                    {activeTab === "artifacts" && localPackageBase && currentRepository &&
                        <ArtifactsTab
                            currentVersion={pkg.version}
                            packageBase={localPackageBase}
                            repository={currentRepository}
                        />
                    }
                </>
            }
        </DialogContent>

        <PackageInfoActions
            isAuthorized={isAuthorized}
            isHeld={status?.is_held ?? false}
            onHoldToggle={() => void handleHoldToggle()}
            onRefreshDatabaseChange={setRefreshDatabase}
            onRemove={() => void handleRemove()}
            onUpdate={() => void handleUpdate()}
            refreshDatabase={refreshDatabase}
        />
    </Dialog>;
}
