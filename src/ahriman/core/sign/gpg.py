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
import requests

from collections.abc import Generator
from pathlib import Path

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import BuildError
from ahriman.core.log import LazyLogging
from ahriman.core.util import check_output, exception_response_text
from ahriman.models.sign_settings import SignSettings


class GPG(LazyLogging):
    """
    gnupg wrapper

    Attributes:
        DEFAULT_TIMEOUT(int): (class attribute) HTTP request timeout in seconds
        configuration(Configuration): configuration instance
        default_key(str | None): default PGP key ID to use
        targets(set[SignSettings]): list of targets to sign (repository, package etc)
    """

    _check_output = check_output
    DEFAULT_TIMEOUT = 30

    def __init__(self, configuration: Configuration) -> None:
        """
        default constructor

        Args:
            configuration(Configuration): configuration instance
        """
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

    def key_download(self, server: str, key: str) -> str:
        """
        download key from public PGP server

        Args:
            server(str): public PGP server which will be used to download the key
            key(str): key ID to download

        Returns:
            str: key as plain text
        """
        key = key if key.startswith("0x") else f"0x{key}"
        try:
            response = requests.get(f"https://{server}/pks/lookup", params={
                "op": "get",
                "options": "mr",
                "search": key
            }, timeout=self.DEFAULT_TIMEOUT)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.logger.exception("could not download key %s from %s: %s", key, server, exception_response_text(e))
            raise
        return response.text

    def key_export(self, key: str) -> str:
        """
        export public key from stored keychain

        Args:
            key(str): key ID to export

        Returns:
            str: PGP key in .asc format
        """
        return GPG._check_output("gpg", "--armor", "--no-emit-version", "--export", key, logger=self.logger)

    def key_fingerprint(self, key: str) -> str:
        """
        get full key fingerprint from short key id

        Args:
            key(str): key ID to lookup

        Returns:
            str: full PGP key fingerprint
        """
        metadata = GPG._check_output("gpg", "--with-colons", "--fingerprint", key, logger=self.logger)
        # fingerprint line will be like
        # fpr:::::::::43A663569A07EE1E4ECC55CC7E3A4240CE3C45C2:
        fingerprint = next(filter(lambda line: line[:3] == "fpr", metadata.splitlines()))
        return fingerprint.split(":")[-2]

    def key_import(self, server: str, key: str) -> None:
        """
        import key to current user and sign it locally

        Args:
            server(str): public PGP server which will be used to download the key
            key(str): key ID to import
        """
        key_body = self.key_download(server, key)
        GPG._check_output("gpg", "--import", input_data=key_body, logger=self.logger)

    def keys(self) -> list[str]:
        """
        extract list of keys described in configuration

        Returns:
            list[str]: list of unique keys which are set in configuration
        """
        def generator() -> Generator[str, None, None]:
            if self.default_key is not None:
                yield self.default_key
            for _, value in filter(lambda pair: pair[0].startswith("key_"), self.configuration["sign"].items()):
                yield value

        return sorted(set(generator()))

    def process(self, path: Path, key: str) -> list[Path]:
        """
        gpg command wrapper

        Args:
            path(Path): path to file to sign
            key(str): PGP key ID

        Returns:
            list[Path]: list of generated files including original file
        """
        GPG._check_output(
            *GPG.sign_command(path, key),
            exception=BuildError(path.name),
            logger=self.logger)
        return [path, path.parent / f"{path.name}.sig"]

    def process_sign_package(self, path: Path, package_base: str) -> list[Path]:
        """
        sign package if required by configuration

        Args:
            path(Path): path to file to sign
            package_base(str): package base required to check for key overrides

        Returns:
            list[Path]: list of generated files including original file
        """
        if SignSettings.Packages not in self.targets:
            return [path]
        key = self.configuration.get("sign", f"key_{package_base}", fallback=self.default_key)
        if key is None:
            self.logger.error("no default key set, skip package %s sign", path)
            return [path]
        return self.process(path, key)

    def process_sign_repository(self, path: Path) -> list[Path]:
        """
        sign repository if required by configuration

        Note:
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
