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
import PersonIcon from "@mui/icons-material/Person";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    IconButton,
    InputAdornment,
    TextField,
} from "@mui/material";
import { ApiError } from "api/client/ApiError";
import DialogHeader from "components/common/DialogHeader";
import { useAuth } from "hooks/useAuth";
import { useNotification } from "hooks/useNotification";
import React, { useState } from "react";

interface LoginDialogProps {
    onClose: () => void;
    open: boolean;
}

export default function LoginDialog({ onClose, open }: LoginDialogProps): React.JSX.Element {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const { login } = useAuth();
    const { showSuccess, showError } = useNotification();

    const handleClose = (): void => {
        setUsername("");
        setPassword("");
        setShowPassword(false);
        onClose();
    };

    const handleSubmit = async (): Promise<void> => {
        if (!username || !password) {
            return;
        }
        try {
            await login(username, password);
            handleClose();
            showSuccess("Logged in", `Successfully logged in as ${username}`);
        } catch (exception) {
            const detail = ApiError.errorDetail(exception);
            if (username === "admin" && password === "admin") {
                showError("Login error", "You've entered a password for user \"root\", did you make a typo in username?");
            } else {
                showError("Login error", `Could not login as ${username}: ${detail}`);
            }
        }
    };

    return <Dialog fullWidth maxWidth="xs" onClose={handleClose} open={open}>
        <DialogHeader onClose={handleClose}>
            Login
        </DialogHeader>

        <DialogContent>
            <TextField
                autoFocus
                fullWidth
                label="username"
                margin="normal"
                onChange={event => setUsername(event.target.value)}
                value={username}
            />
            <TextField
                fullWidth
                label="password"
                margin="normal"
                onChange={event => setPassword(event.target.value)}
                onKeyDown={event => {
                    if (event.key === "Enter") {
                        void handleSubmit();
                    }
                }}
                slotProps={{
                    input: {
                        endAdornment:
                            <InputAdornment position="end">
                                <IconButton
                                    aria-label={showPassword ? "Hide password" : "Show password"}
                                    edge="end"
                                    onClick={() => setShowPassword(!showPassword)}
                                    size="small"
                                >
                                    {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                                </IconButton>
                            </InputAdornment>,
                    },
                }}
                type={showPassword ? "text" : "password"}
                value={password}
            />
        </DialogContent>

        <DialogActions>
            <Button onClick={() => void handleSubmit()} startIcon={<PersonIcon />} variant="contained">login</Button>
        </DialogActions>
    </Dialog>;
}
