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
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import {
    Autocomplete,
    Box,
    Button,
    Checkbox,
    Dialog,
    DialogActions,
    DialogContent,
    FormControlLabel,
    IconButton,
    TextField,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { ApiError } from "api/client/ApiError";
import DialogHeader from "components/common/DialogHeader";
import RepositorySelect from "components/common/RepositorySelect";
import { QueryKeys } from "hooks/QueryKeys";
import { useClient } from "hooks/useClient";
import { useDebounce } from "hooks/useDebounce";
import { useNotification } from "hooks/useNotification";
import { useSelectedRepository } from "hooks/useSelectedRepository";
import type { AURPackage } from "models/AURPackage";
import type { PackageActionRequest } from "models/PackageActionRequest";
import React, { useRef, useState } from "react";

interface EnvironmentVariable {
    id: number;
    key: string;
    value: string;
}

interface PackageAddDialogProps {
    open: boolean;
    onClose: () => void;
}

export default function PackageAddDialog({ open, onClose }: PackageAddDialogProps): React.JSX.Element {
    const client = useClient();
    const { showSuccess, showError } = useNotification();
    const repositorySelect = useSelectedRepository();

    const [packageName, setPackageName] = useState("");
    const [refreshDatabase, setRefreshDatabase] = useState(true);
    const [environmentVariables, setEnvironmentVariables] = useState<EnvironmentVariable[]>([]);
    const variableIdCounter = useRef(0);

    const handleClose = (): void => {
        setPackageName("");
        repositorySelect.reset();
        setRefreshDatabase(true);
        setEnvironmentVariables([]);
        onClose();
    };

    const debouncedSearch = useDebounce(packageName, 500);

    const { data: searchResults = [] } = useQuery<AURPackage[]>({
        queryKey: QueryKeys.search(debouncedSearch),
        queryFn: () => client.service.servicePackageSearch(debouncedSearch),
        enabled: debouncedSearch.length >= 3,
    });

    const handleSubmit = async (action: "add" | "request"): Promise<void> => {
        if (!packageName) {
            return;
        }
        const repository = repositorySelect.selectedRepository;
        if (!repository) {
            return;
        }
        try {
            const patches = environmentVariables.filter(variable => variable.key);
            const request: PackageActionRequest = { packages: [packageName], patches };
            if (action === "add") {
                request.refresh = refreshDatabase;
                await client.service.servicePackageAdd(repository, request);
            } else {
                await client.service.servicePackageRequest(repository, request);
            }
            handleClose();
            showSuccess("Success", `Packages ${packageName} have been ${action === "add" ? "added" : "requested"}`);
        } catch (exception) {
            const detail = ApiError.errorDetail(exception);
            showError("Action failed", `Package ${action} failed: ${detail}`);
        }
    };

    return <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogHeader onClose={handleClose}>
            Add new packages
        </DialogHeader>

        <DialogContent>
            <RepositorySelect repositorySelect={repositorySelect} />

            <Autocomplete
                freeSolo
                options={searchResults.map(pkg => pkg.package)}
                inputValue={packageName}
                onInputChange={(_, value) => setPackageName(value)}
                renderOption={(props, option) => {
                    const pkg = searchResults.find(pkg => pkg.package === option);
                    return (
                        <li {...props} key={option}>
                            {option}{pkg ? ` (${pkg.description})` : ""}
                        </li>
                    );
                }}
                renderInput={params =>
                    <TextField {...params} label="package" placeholder="AUR package" margin="normal" />
                }
            />

            <FormControlLabel
                control={<Checkbox checked={refreshDatabase} onChange={(_, checked) => setRefreshDatabase(checked)} />}
                label="update pacman databases"
            />

            <Button
                fullWidth
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={() => {
                    const id = variableIdCounter.current++;
                    setEnvironmentVariables(prev => [...prev, { id, key: "", value: "" }]);
                }}
                sx={{ mt: 1 }}
            >
                add environment variable
            </Button>

            {environmentVariables.map(variable =>
                <Box key={variable.id} sx={{ display: "flex", gap: 1, mt: 1, alignItems: "center" }}>
                    <TextField
                        size="small"
                        placeholder="name"
                        value={variable.key}
                        onChange={event => {
                            const newKey = event.target.value;
                            setEnvironmentVariables(prev =>
                                prev.map(entry => entry.id === variable.id ? { ...entry, key: newKey } : entry),
                            );
                        }}
                        sx={{ flex: 1 }}
                    />
                    <Box>=</Box>
                    <TextField
                        size="small"
                        placeholder="value"
                        value={variable.value}
                        onChange={event => {
                            const newValue = event.target.value;
                            setEnvironmentVariables(prev =>
                                prev.map(entry => entry.id === variable.id ? { ...entry, value: newValue } : entry),
                            );
                        }}
                        sx={{ flex: 1 }}
                    />
                    <IconButton size="small" color="error" aria-label="Remove variable" onClick={() => setEnvironmentVariables(prev => prev.filter(entry => entry.id !== variable.id))}>
                        <DeleteIcon />
                    </IconButton>
                </Box>,
            )}
        </DialogContent>

        <DialogActions>
            <Button onClick={() => void handleSubmit("add")} variant="contained" startIcon={<PlayArrowIcon />}>add</Button>
            <Button onClick={() => void handleSubmit("request")} variant="contained" color="success" startIcon={<AddIcon />}>request</Button>
        </DialogActions>
    </Dialog>;
}
