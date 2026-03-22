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
import CodeBlock from "components/common/CodeBlock";
import { usePackageChanges } from "hooks/usePackageChanges";
import type { RepositoryId } from "models/RepositoryId";
import React from "react";

interface PkgbuildTabProps {
    packageBase: string;
    repository: RepositoryId;
}

export default function PkgbuildTab({ packageBase, repository }: PkgbuildTabProps): React.JSX.Element {
    const data = usePackageChanges(packageBase, repository);

    return <CodeBlock content={data?.pkgbuild ?? ""} height={400} language="bash" />;
}
