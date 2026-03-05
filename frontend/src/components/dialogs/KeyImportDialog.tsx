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
import RefreshIcon from "@mui/icons-material/Refresh";
import {
    Box,
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    TextField,
} from "@mui/material";
import { ApiError } from "api/client/ApiError";
import CodeBlock from "components/common/CodeBlock";
import DialogHeader from "components/common/DialogHeader";
import { useClient } from "hooks/useClient";
import { useNotification } from "hooks/useNotification";
import React, { useState } from "react";

interface KeyImportDialogProps {
    open: boolean;
    onClose: () => void;
}

export default function KeyImportDialog({ open, onClose }: KeyImportDialogProps): React.JSX.Element {
    const client = useClient();
    const { showSuccess, showError } = useNotification();

    const [fingerprint, setFingerprint] = useState("");
    const [server, setServer] = useState("keyserver.ubuntu.com");
    const [keyBody, setKeyBody] = useState("");

    const handleClose = (): void => {
        setFingerprint("");
        setServer("keyserver.ubuntu.com");
        setKeyBody("");
        onClose();
    };

    const handleFetch: () => Promise<void> = async () => {
        if (!fingerprint || !server) {
            return;
        }
        try {
            const result = await client.service.servicePGPFetch(fingerprint, server);
            setKeyBody(result.key);
        } catch (exception) {
            const detail = ApiError.errorDetail(exception);
            showError("Action failed", `Could not fetch key: ${detail}`);
        }
    };

    const handleImport: () => Promise<void> = async () => {
        if (!fingerprint || !server) {
            return;
        }
        try {
            await client.service.servicePGPImport({ key: fingerprint, server });
            handleClose();
            showSuccess("Success", `Key ${fingerprint} has been imported`);
        } catch (exception) {
            const detail = ApiError.errorDetail(exception);
            showError("Action failed", `Could not import key ${fingerprint} from ${server}: ${detail}`);
        }
    };

    return <Dialog open={open} onClose={handleClose} maxWidth="lg" fullWidth>
        <DialogHeader onClose={handleClose}>
            Import key from PGP server
        </DialogHeader>

        <DialogContent>
            <TextField
                label="fingerprint"
                placeholder="PGP key fingerprint"
                fullWidth
                margin="normal"
                value={fingerprint}
                onChange={event => setFingerprint(event.target.value)}
            />
            <TextField
                label="key server"
                placeholder="PGP key server"
                fullWidth
                margin="normal"
                value={server}
                onChange={event => setServer(event.target.value)}
            />
            {keyBody &&
                <Box sx={{ mt: 2 }}>
                    <CodeBlock getText={() => keyBody} height={300} />
                </Box>
            }
        </DialogContent>

        <DialogActions>
            <Button onClick={() => void handleImport()} variant="contained" startIcon={<PlayArrowIcon />}>import</Button>
            <Button onClick={() => void handleFetch()} variant="contained" color="success" startIcon={<RefreshIcon />}>fetch</Button>
        </DialogActions>
    </Dialog>;
}
