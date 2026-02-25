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
import { type RefObject, useCallback, useRef } from "react";

interface UseAutoScrollResult {
    preRef: RefObject<HTMLElement | null>;
    handleScroll: () => void;
    scrollToBottom: () => void;
    resetScroll: () => void;
}

export function useAutoScroll(): UseAutoScrollResult {
    const preRef = useRef<HTMLElement>(null);
    const initialScrollDone = useRef(false);
    const wasAtBottom = useRef(true);

    const handleScroll = useCallback((): void => {
        if (preRef.current) {
            const element = preRef.current;
            wasAtBottom.current = element.scrollTop + element.clientHeight >= element.scrollHeight - 50;
        }
    }, []);

    const resetScroll = useCallback((): void => {
        initialScrollDone.current = false;
    }, []);

    // scroll to bottom on initial load, then only if already near bottom and no active text selection
    const scrollToBottom = useCallback((): void => {
        if (!preRef.current) {
            return;
        }
        const element = preRef.current;
        if (!initialScrollDone.current) {
            element.scrollTop = element.scrollHeight;
            initialScrollDone.current = true;
        } else {
            const hasSelection = !document.getSelection()?.isCollapsed;
            if (wasAtBottom.current && !hasSelection) {
                element.scrollTop = element.scrollHeight;
            }
        }
    }, []);

    return { preRef, handleScroll, scrollToBottom, resetScroll };
}
