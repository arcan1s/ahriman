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
import GitHubIcon from "@mui/icons-material/GitHub";
import HomeIcon from "@mui/icons-material/Home";
import LoginIcon from "@mui/icons-material/Login";
import LogoutIcon from "@mui/icons-material/Logout";
import { Box, Button, Link, Typography } from "@mui/material";
import { useAuth } from "hooks/useAuth";
import type React from "react";

interface FooterProps {
    docsEnabled: boolean;
    indexUrl?: string;
    onLoginClick: () => void;
    version: string;
}

export default function Footer({ docsEnabled, indexUrl, onLoginClick, version }: FooterProps): React.JSX.Element {
    const { enabled: authEnabled, username, logout } = useAuth();

    return <Box
        component="footer"
        sx={{
            alignItems: "center",
            borderColor: "divider",
            borderTop: 1,
            display: "flex",
            flexWrap: "wrap",
            justifyContent: "space-between",
            mt: 2,
            py: 1,
        }}
    >
        <Box sx={{ alignItems: "center", display: "flex", gap: 2 }}>
            <Link color="inherit" href="https://github.com/arcan1s/ahriman" sx={{ alignItems: "center", display: "flex", gap: 0.5 }} underline="hover">
                <GitHubIcon fontSize="small" />
                <Typography variant="body2">ahriman {version}</Typography>
            </Link>
            <Link color="text.secondary" href="https://github.com/arcan1s/ahriman/releases" underline="hover" variant="body2">
                releases
            </Link>
            <Link color="text.secondary" href="https://github.com/arcan1s/ahriman/issues" underline="hover" variant="body2">
                report a bug
            </Link>
            {docsEnabled &&
                <Link color="text.secondary" href="/api-docs" underline="hover" variant="body2">
                    api
                </Link>
            }
        </Box>

        {indexUrl &&
            <Box>
                <Link color="inherit" href={indexUrl} underline="hover" sx={{ alignItems: "center", display: "flex", gap: 0.5 }}>
                    <HomeIcon fontSize="small" />
                    <Typography variant="body2">repo index</Typography>
                </Link>
            </Box>
        }

        {authEnabled &&
            <Box>
                {username ?
                    <Button onClick={() => void logout()} size="small" startIcon={<LogoutIcon />} sx={{ textTransform: "none" }}>
                        logout ({username})
                    </Button>
                    :
                    <Button onClick={onLoginClick} size="small" startIcon={<LoginIcon />} sx={{ textTransform: "none" }}>
                        login
                    </Button>
                }
            </Box>
        }
    </Box>;
}
