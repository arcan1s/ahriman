#
# Copyright (c) 2021-2025 ahriman team.
#
# This file is part of ahriman
# (see https://github.com/arcan1s/ahriman).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import argparse
import shutil
import site
import sys

from pathlib import Path


prefix = Path(sys.prefix).relative_to("/")
site_packages = Path(site.getsitepackages()[0]).relative_to("/")
SUBPACKAGES = {
    "ahriman-core": [
        prefix / "bin",
        prefix / "lib" / "systemd",
        prefix / "share",
        site_packages,
    ],
    "ahriman-triggers": [
        prefix / "share" / "ahriman" / "settings" / "ahriman.ini.d" / "00-triggers.ini",
        site_packages / "ahriman" / "application" / "handlers" / "triggers_support.py",
        site_packages / "ahriman" / "core" / "distributed",
        site_packages / "ahriman" / "core" / "support",
    ],
    "ahriman-web": [
        prefix / "lib" / "systemd" / "system" / "ahriman-web.service",
        prefix / "lib" / "systemd" / "system" / "ahriman-web@.service",
        prefix / "share" / "ahriman" / "settings" / "ahriman.ini.d" / "00-web.ini",
        prefix / "share" / "ahriman" / "templates" / "api.jinja2",
        prefix / "share" / "ahriman" / "templates" / "build-status",
        prefix / "share" / "ahriman" / "templates" / "build-status.jinja2",
        prefix / "share" / "ahriman" / "templates" / "error.jinja2",
        site_packages / "ahriman" / "application" / "handlers" / "web.py",
        site_packages / "ahriman" / "core" / "auth",
        site_packages / "ahriman" / "web",
    ],
}


def subpackages(root: Path) -> dict[str, list[Path]]:
    """
    extend list of subpackages

    Args:
        root(Path): root directory

    Returns:
        dict[str, list[Path]]: extended list of files which belong to a specific package
    """
    for paths in SUBPACKAGES.values():
        new_paths = []
        for path in paths:
            full_path = root / path

            match path.suffix:
                case ".py":
                    pycache_path = full_path.parent / "__pycache__"
                    new_paths.extend(
                        new_path.relative_to(root) for new_path in pycache_path.glob(f"{full_path.stem}.*.pyc")
                    )

        paths.extend(new_paths)

    return SUBPACKAGES


def process(root: Path, include: list[Path], exclude: list[Path]) -> None:
    """
    remove files based on patterns

    Args:
        root(Path): root directory
        include(list[Path]): list of files to include to the subpackage
        exclude(list[Path]): list of files to exclude from the subpackage
    """
    for subdirectory, _, files in root.walk(top_down=False):
        for file in files:
            full_path = subdirectory / file
            relative_path = full_path.relative_to(root)

            if not any(relative_path.is_relative_to(path) for path in include):
                full_path.unlink()
            elif any(relative_path.is_relative_to(path) for path in exclude):
                full_path.unlink()

        content = list(subdirectory.iterdir())
        if not content:
            shutil.rmtree(subdirectory)


def run() -> None:
    """
    run application
    """
    parser = argparse.ArgumentParser(description="Split package into subpackages")
    parser.add_argument("root", help="package root", type=Path)
    parser.add_argument("subpackage", help="subpackage name", choices=SUBPACKAGES.keys())

    args = parser.parse_args()

    full_subpackages = subpackages(args.root)
    include = full_subpackages[args.subpackage]
    exclude = [
        path
        for subpackage, portion in full_subpackages.items()
        if subpackage != args.subpackage
        for path in portion
        if not any(include_path.is_relative_to(path) for include_path in include)
    ]

    process(args.root, include, exclude)


if __name__ == "__main__":
    run()
