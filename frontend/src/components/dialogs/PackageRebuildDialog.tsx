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
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import { Button, Dialog, DialogActions, DialogContent, TextField } from "@mui/material";
import { ApiError } from "api/client/ApiError";
import DialogHeader from "components/common/DialogHeader";
import RepositorySelect from "components/common/RepositorySelect";
import { useClient } from "hooks/useClient";
import { useNotification } from "hooks/useNotification";
import { useSelectedRepository } from "hooks/useSelectedRepository";
import React, { useState } from "react";

interface PackageRebuildDialogProps {
    onClose: () => void;
    open: boolean;
}

export default function PackageRebuildDialog({ onClose, open }: PackageRebuildDialogProps): React.JSX.Element {
    const client = useClient();
    const { showSuccess, showError } = useNotification();
    const repositorySelect = useSelectedRepository();

    const [dependency, setDependency] = useState("");

    const handleClose = (): void => {
        setDependency("");
        repositorySelect.reset();
        onClose();
    };

    const handleRebuild = async (): Promise<void> => {
        if (!dependency) {
            return;
        }
        const repository = repositorySelect.selectedRepository;
        if (!repository) {
            return;
        }
        try {
            await client.service.serviceRebuild(repository, [dependency]);
            handleClose();
            showSuccess("Success", `Repository rebuild has been run for packages which depend on ${dependency}`);
        } catch (exception) {
            const detail = ApiError.errorDetail(exception);
            showError("Action failed", `Repository rebuild failed: ${detail}`);
        }
    };

    return <Dialog fullWidth maxWidth="md" onClose={handleClose} open={open}>
        <DialogHeader onClose={handleClose}>
            Rebuild depending packages
        </DialogHeader>

        <DialogContent>
            <RepositorySelect repositorySelect={repositorySelect} />

            <TextField
                fullWidth
                label="dependency"
                margin="normal"
                placeholder="packages dependency"
                onChange={event => setDependency(event.target.value)}
                value={dependency}
            />
        </DialogContent>

        <DialogActions>
            <Button onClick={() => void handleRebuild()} startIcon={<PlayArrowIcon />} variant="contained">rebuild</Button>
        </DialogActions>
    </Dialog>;
}
