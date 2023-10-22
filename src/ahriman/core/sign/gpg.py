#
# Copyright (c) 2021-2023 ahriman team.
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

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import BuildError
from ahriman.core.http import SyncHttpClient
from ahriman.core.util import check_output
from ahriman.models.sign_settings import SignSettings


class GPG(SyncHttpClient):
    """
    gnupg wrapper

    Attributes:
        configuration(Configuration): configuration instance
        default_key(str | None): default PGP key ID to use
        targets(set[SignSettings]): list of targets to sign (repository, package etc.)
    """

    def __init__(self, configuration: Configuration) -> None:
        """
        default constructor

        Args:
            configuration(Configuration): configuration instance
        """
        SyncHttpClient.__init__(self)
        self.configuration = configuration
        self.targets, self.default_key = self.sign_options(configuration)

    @property
    def repository_sign_args(self) -> list[str]:
        """
        get command line arguments based on settings

        Returns:
            list[str]: command line arguments for repo-add command to sign database
        """
        if SignSettings.Repository not in self.targets:
            return []
        if self.default_key is None:
            self.logger.error("no default key set, skip repository sign")
            return []
        return ["--sign", "--key", self.default_key]

    @staticmethod
    def sign_command(path: Path, key: str) -> list[str]:
        """
        gpg command to run

        Args:
            path(Path): path to file to sign
            key(str): PGP key ID

        Returns:
            list[str]: gpg command with all required arguments
        """
        return ["gpg", "-u", key, "-b", str(path)]

    @staticmethod
    def sign_options(configuration: Configuration) -> tuple[set[SignSettings], str | None]:
        """
        extract default sign options from configuration

        Args:
            configuration(Configuration): configuration instance

        Returns:
            tuple[set[SignSettings], str | None]: tuple of sign targets and default PGP key
        """
        targets: set[SignSettings] = set()
        for option in configuration.getlist("sign", "target", fallback=[]):
            target = SignSettings.from_option(option)
            if target == SignSettings.Disabled:
                continue
            targets.add(target)
        default_key = configuration.get("sign", "key") if targets else None
        return targets, default_key

    @staticmethod
    def signature(filepath: Path) -> Path:
        """
        generate signature name for the file

        Args:
            filepath(Path): path to the file which will be signed

        Returns:
            str: path to signature file
        """
        return filepath.parent / f"{filepath.name}.sig"

    def key_download(self, server: str, key: str) -> str:
        """
        download key from public PGP server

        Args:
            server(str): public PGP server which will be used to download data
            key(str): key ID to download

        Returns:
            str: key as plain text
        """
        key = key if key.startswith("0x") else f"0x{key}"
        response = self.make_request("GET", f"https://{server}/pks/lookup", params=[
            ("op", "get"),
            ("options", "mr"),
            ("search", key),
        ])
        return response.text

    def key_export(self, key: str) -> str:
        """
        export public key from stored keychain

        Args:
            key(str): key ID to export

        Returns:
            str: PGP key in .asc format
        """
        return check_output("gpg", "--armor", "--no-emit-version", "--export", key, logger=self.logger)

    def key_fingerprint(self, key: str) -> str:
        """
        get full key fingerprint from short key id

        Args:
            key(str): key ID to lookup

        Returns:
            str: full PGP key fingerprint
        """
        metadata = check_output("gpg", "--with-colons", "--fingerprint", key, logger=self.logger)
        # fingerprint line will be like
        # fpr:::::::::43A663569A07EE1E4ECC55CC7E3A4240CE3C45C2:
        fingerprint = next(filter(lambda line: line[:3] == "fpr", metadata.splitlines()))
        return fingerprint.split(":")[-2]

    def key_import(self, server: str, key: str) -> None:
        """
        import key to current user and sign it locally

        Args:
            server(str): public PGP server which will be used to download data
            key(str): key ID to import
        """
        key_body = self.key_download(server, key)
        check_output("gpg", "--import", input_data=key_body, logger=self.logger)

    def process(self, path: Path, key: str) -> list[Path]:
        """
        gpg command wrapper

        Args:
            path(Path): path to file to sign
            key(str): PGP key ID

        Returns:
            list[Path]: list of generated files including original file
        """
        check_output(
            *GPG.sign_command(path, key),
            exception=BuildError.from_process(path.name),
            logger=self.logger)
        return [path, self.signature(path)]

    def process_sign_package(self, path: Path, packager_key: str | None) -> list[Path]:
        """
        sign package if required by configuration and signature doesn't exist

        Args:
            path(Path): path to file to sign
            packager_key(str | None): optional packager key to sign

        Returns:
            list[Path]: list of generated files including original file
        """
        if (signature := self.signature(path)).is_file():
            # the file was already signed before, just use its signature
            return [path, signature]

        if SignSettings.Packages not in self.targets:
            return [path]

        key = packager_key or self.default_key
        if key is None:
            self.logger.error("no default key set, skip package %s sign", path)
            return [path]
        return self.process(path, key)

    def process_sign_repository(self, path: Path) -> list[Path]:
        """
        sign repository if required by configuration

        Notes:
            More likely you just want to pass ``repository_sign_args`` to repo wrapper

        Args:
            path(Path): path to repository database

        Returns:
            list[Path]: list of generated files including original file
        """
        if SignSettings.Repository not in self.targets:
            return [path]
        if self.default_key is None:
            self.logger.error("no default key set, skip repository sign")
            return [path]
        return self.process(path, self.default_key)
