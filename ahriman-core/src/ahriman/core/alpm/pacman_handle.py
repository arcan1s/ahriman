#
# Copyright (c) 2021-2026 ahriman team.
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
from pathlib import Path
from pyalpm import Handle, Package  # type: ignore[import-not-found]
from tempfile import TemporaryDirectory
from typing import Any, ClassVar, Self


class PacmanHandle:
    """
    lightweight wrapper for pacman handle to be used for direct alpm operations (e.g. package load)

    Attributes:
        handle(Handle): pyalpm handle instance
    """

    _ephemeral: ClassVar[Self | None] = None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Args:
            *args(Any): positional arguments for :class:`pyalpm.Handle`
            **kwargs(Any): keyword arguments for :class:`pyalpm.Handle`
        """
        self.handle = Handle(*args, **kwargs)

    @classmethod
    def ephemeral(cls) -> Self:
        """
        create temporary instance with no access to real databases

        Returns:
            Self: loaded class
        """
        if cls._ephemeral is None:
            # handle creates alpm version file, but we don't use it
            # so it is ok to just remove it
            with TemporaryDirectory(ignore_cleanup_errors=True) as dir_name:
                cls._ephemeral = cls("/", dir_name)
        return cls._ephemeral

    def package_load(self, path: Path) -> Package:
        """
        load package from path to the archive

        Args:
            path(Path): path to package archive

        Returns:
            Package: package instance
        """
        return self.handle.load_pkg(str(path))

    def __getattr__(self, item: str) -> Any:
        """
        proxy methods for :class:`pyalpm.Handle`, because it doesn't allow subclassing

        Args:
            item(str): property name

        Returns:
            Any: attribute by its name
        """
        return self.handle.__getattribute__(item)
