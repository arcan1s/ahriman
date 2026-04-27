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
import { useQueryClient } from "@tanstack/react-query";
import { useEventStream } from "hooks/useEventStream";
import { useRepository } from "hooks/useRepository";
import type { ReactNode } from "react";

export function EventStreamProvider({ children }: { children: ReactNode }): ReactNode {
    const queryClient = useQueryClient();
    const { currentRepository } = useRepository();

    useEventStream(queryClient, currentRepository);

    return children;
}
