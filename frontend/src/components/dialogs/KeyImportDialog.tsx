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
    onClose: () => void;
    open: boolean;
}

export default function KeyImportDialog({ onClose, open }: KeyImportDialogProps): React.JSX.Element {
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

    const handleFetch = async (): Promise<void> => {
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

    const handleImport = async (): Promise<void> => {
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

    return <Dialog fullWidth maxWidth="lg" onClose={handleClose} open={open}>
        <DialogHeader onClose={handleClose}>
            Import key from PGP server
        </DialogHeader>

        <DialogContent>
            <TextField
                fullWidth
                label="fingerprint"
                margin="normal"
                onChange={event => setFingerprint(event.target.value)}
                placeholder="PGP key fingerprint"
                value={fingerprint}
            />
            <TextField
                fullWidth
                label="key server"
                margin="normal"
                onChange={event => setServer(event.target.value)}
                placeholder="PGP key server"
                value={server}
            />
            {keyBody &&
                <Box sx={{ mt: 2 }}>
                    <CodeBlock height={300} content={keyBody} />
                </Box>
            }
        </DialogContent>

        <DialogActions>
            <Button onClick={() => void handleImport()} startIcon={<PlayArrowIcon />} variant="contained">import</Button>
            <Button color="success" onClick={() => void handleFetch()} startIcon={<RefreshIcon />} variant="contained">fetch</Button>
        </DialogActions>
    </Dialog>;
}
