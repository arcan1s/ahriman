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
import { Alert, Slide } from "@mui/material";
import type { Notification } from "models/Notification";
import React, { useEffect, useState } from "react";

interface NotificationItemProps {
    notification: Notification;
    onClose: (id: string) => void;
}

export default function NotificationItem({ notification, onClose }: NotificationItemProps): React.JSX.Element {
    const [show, setShow] = useState(true);

    useEffect(() => {
        const timer = setTimeout(() => setShow(false), 5000);
        return () => clearTimeout(timer);
    }, []);

    return (
        <Slide direction="down" in={show} mountOnEnter unmountOnExit onExited={() => onClose(notification.id)}>
            <Alert
                onClose={() => setShow(false)}
                severity={notification.severity}
                variant="filled"
                sx={{ width: "100%", pointerEvents: "auto" }}
            >
                <strong>{notification.title}</strong>
                {notification.message && ` - ${notification.message}`}
            </Alert>
        </Slide>
    );
}
