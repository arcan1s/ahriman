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
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, ClassVar, IO, Self
from urllib.parse import urlparse

from ahriman.core.alpm.pkgbuild_parser import PkgbuildParser, PkgbuildToken
from ahriman.core.utils import srcinfo_property_list
from ahriman.models.pkgbuild_patch import PkgbuildPatch


@dataclass(frozen=True)
class Pkgbuild(Mapping[str, Any]):
    """
    model and proxy for PKGBUILD properties

    Attributes:
        DEFAULT_ENCODINGS(str): (class attribute) default encoding to be applied on the file content
        fields(dict[str, PkgbuildPatch]): PKGBUILD fields
    """

    fields: dict[str, PkgbuildPatch]

    DEFAULT_ENCODINGS: ClassVar[str] = "utf8"

    @property
    def variables(self) -> dict[str, str]:
        """
        list of variables defined and (maybe) used in this PKGBUILD

        Returns:
            dict[str, str]: map of variable name to its value. The value will be included here in case if it presented
            in the internal dictionary, it is not a function and the value has string type
        """
        return {
            key: value.value
            for key, value in self.fields.items()
            if not value.is_function and isinstance(value.value, str)
        }

    @classmethod
    def from_file(cls, path: Path, encoding: str | None = None) -> Self:
        """
        parse PKGBUILD from the file

        Args:
            path(Path): path to the PKGBUILD file
            encoding(str | None, optional): the encoding of the file (Default value = None)

        Returns:
            Self: constructed instance of self

        Raises:
            EncodeError: if encoding is unknown
        """
        # read raw bytes from file
        with path.open("rb") as input_file:
            content = input_file.read()

        # decode bytes content based on either
        encoding = encoding or cls.DEFAULT_ENCODINGS
        io = StringIO(content.decode(encoding, errors="backslashreplace"))

        return cls.from_io(io)

    @classmethod
    def from_io(cls, stream: IO[str]) -> Self:
        """
        parse PKGBUILD from input stream

        Args:
            stream(IO[str]): input stream containing PKGBUILD content

        Returns:
            Self: constructed instance of self
        """
        parser = PkgbuildParser(stream)
        fields = {patch.key: patch for patch in parser.parse()}

        # pkgbase is optional field, the pkgname must be used instead if not set
        # however, pkgname is not presented is "package()" functions which we are parsing here too,
        # thus, in our terms, it is optional too
        if "pkgbase" not in fields and "pkgname" in fields:
            fields["pkgbase"] = PkgbuildPatch("pkgbase", fields["pkgname"].value)

        return cls({key: value for key, value in fields.items() if key})

    @staticmethod
    def local_files(path: Path) -> Iterator[Path]:
        """
        extract list of local files

        Args:
            path(Path): path to package sources directory

        Yields:
            Path: list of paths of files which belong to the package and distributed together with this tarball.
            All paths are relative to the ``path``

        Raises:
            PackageInfoError: if there are parsing errors
        """
        pkgbuild = Pkgbuild.from_file(path / "PKGBUILD")
        # we could use arch property, but for consistency it is better to call special method
        architectures = Pkgbuild.supported_architectures(path)

        for architecture in architectures:
            for source in srcinfo_property_list("source", pkgbuild, {}, architecture=architecture):
                if "::" in source:
                    _, source = source.split("::", maxsplit=1)  # in case if filename is specified, remove it

                if urlparse(source).scheme:
                    # basically file schema should use absolute path which is impossible if we are distributing
                    # files together with PKGBUILD. In this case we are going to skip it also
                    continue

                yield Path(source)

        if (install := pkgbuild.get("install")) is not None:
            yield Path(install)

    @staticmethod
    def supported_architectures(path: Path) -> set[str]:
        """
        load supported architectures from package sources

        Args:
            path(Path): path to package sources directory

        Returns:
            set[str]: list of package supported architectures
        """
        pkgbuild = Pkgbuild.from_file(path / "PKGBUILD")
        return set(pkgbuild.get("arch", []))

    def packages(self) -> dict[str, Self]:
        """
        extract properties from internal package functions

        Returns:
            dict[str, Self]: map of package name to its inner properties if defined
        """
        packages = [self["pkgname"]] if isinstance(self["pkgname"], str) else self["pkgname"]

        def io(package_name: str) -> IO[str]:
            # try to read package specific function and fallback to default otherwise
            content = self.get(f"package_{package_name}") or self.get("package") or ""
            return StringIO(content)

        return {package: self.from_io(io(package)) for package in packages}

    def __getitem__(self, item: str) -> Any:
        """
        get the field of the PKGBUILD. This method tries to get exact key value if possible; if none was found,
        it tries to fetch function with the same name

        Args:
            item(str): key name

        Returns:
            Any: substituted value by the key

        Raises:
            KeyError: if key doesn't exist
        """
        value = self.fields.get(item)
        # if the key wasn't found and user didn't ask for function explicitly, we can try to get by function name
        if value is None and not item.endswith(PkgbuildToken.FunctionDeclaration):
            value = self.fields.get(f"{item}{PkgbuildToken.FunctionDeclaration}")

        # if we still didn't find anything, we can just raise the exception
        if value is None:
            raise KeyError(item)

        return value.substitute(self.variables)

    def __iter__(self) -> Iterator[str]:
        """
        iterate over the fields

        Returns:
            Iterator[str]: keys iterator
        """
        return iter(self.fields)

    def __len__(self) -> int:
        """
        get length of the mapping

        Returns:
            int: amount of the fields in this PKGBUILD
        """
        return len(self.fields)
