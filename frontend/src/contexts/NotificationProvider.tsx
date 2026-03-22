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
import { type AlertColor, Box } from "@mui/material";
import NotificationItem from "components/common/NotificationItem";
import { NotificationContext } from "contexts/NotificationContext";
import type { Notification } from "models/Notification";
import React, { type ReactNode, useCallback, useMemo, useState } from "react";

export function NotificationProvider({ children }: { children: ReactNode }): React.JSX.Element {
    const [notifications, setNotifications] = useState<Notification[]>([]);

    const addNotification = useCallback((title: string, message: string, severity: AlertColor) => {
        const id = `${severity}:${title}:${message}`;
        setNotifications(prev => {
            if (prev.some(notification => notification.id === id)) {
                return prev;
            }
            return [...prev, { id, title, message, severity }];
        });
    }, []);

    const removeNotification = useCallback((key: string) => {
        setNotifications(prev => prev.filter(notification => notification.id !== key));
    }, []);

    const showSuccess = useCallback(
        (title: string, message: string) => addNotification(title, message, "success"),
        [addNotification],
    );
    const showError = useCallback(
        (title: string, message: string) => addNotification(title, message, "error"),
        [addNotification],
    );

    const value = useMemo(() => ({ showSuccess, showError }), [showSuccess, showError]);

    return <NotificationContext.Provider value={value}>
        {children}
        <Box
            sx={{
                display: "flex",
                flexDirection: "column",
                gap: 1,
                left: "50%",
                maxWidth: 500,
                pointerEvents: "none",
                position: "fixed",
                top: 16,
                transform: "translateX(-50%)",
                width: "100%",
                zIndex: theme => theme.zIndex.snackbar,
            }}
        >
            {notifications.map(notification =>
                <NotificationItem key={notification.id} notification={notification} onClose={removeNotification} />,
            )}
        </Box>
    </NotificationContext.Provider>;
}
