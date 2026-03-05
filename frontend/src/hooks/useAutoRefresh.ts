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
import { useLocalStorage } from "hooks/useLocalStorage";
import { type Dispatch, type SetStateAction, useEffect, useState } from "react";

interface AutoRefreshResult {
    interval: number;
    setInterval: Dispatch<SetStateAction<number>>;
    setPaused: Dispatch<SetStateAction<boolean>>;
}

export function useAutoRefresh(key: string, defaultInterval: number): AutoRefreshResult {
    const storageKey = `ahriman-${key}`;
    const [interval, setInterval] = useLocalStorage<number>(storageKey, defaultInterval);
    const [paused, setPaused] = useState(false);

    // Apply defaultInterval when it becomes available (e.g. after info endpoint loads)
    // but only if the user hasn't explicitly set a preference
    useEffect(() => {
        if (defaultInterval > 0 && window.localStorage.getItem(storageKey) === null) {
            setInterval(defaultInterval);
        }
    }, [storageKey, defaultInterval, setInterval]);

    const effectiveInterval = paused ? 0 : interval;

    return {
        interval: effectiveInterval,
        setInterval,
        setPaused,
    };
}
