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
import { Box, Tab, Tabs } from "@mui/material";
import { useRepository } from "hooks/useRepository";
import type React from "react";

export default function Navbar(): React.JSX.Element | null {
    const { repositories, currentRepository, setCurrentRepository } = useRepository();

    if (repositories.length === 0 || !currentRepository) {
        return null;
    }

    const currentIndex = repositories.findIndex(repository =>
        repository.architecture === currentRepository.architecture &&
            repository.repository === currentRepository.repository,
    );

    return <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs
            value={currentIndex >= 0 ? currentIndex : 0}
            onChange={(_, newValue: number) => {
                const repository = repositories[newValue];
                if (repository) {
                    setCurrentRepository(repository);
                }
            }}
            variant="scrollable"
            scrollButtons="auto"
        >
            {repositories.map(repository =>
                <Tab
                    key={repository.key}
                    label={repository.label}
                />,
            )}
        </Tabs>
    </Box>;
}
