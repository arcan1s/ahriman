#
# Copyright (c) 2021-2022 ahriman team.
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
import logging
import requests

from pathlib import Path
from typing import List, Optional, Set, Tuple

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import BuildFailed
from ahriman.core.util import check_output, exception_response_text
from ahriman.models.sign_settings import SignSettings


class GPG:
    """
    gnupg wrapper

    Attributes:
        architecture(str): repository architecture
        configuration(Configuration): configuration instance
        default_key(Optional[str]): default PGP key ID to use
        logger(logging.Logger): class logger
        targets(Set[SignSettings]): list of targets to sign (repository, package etc)
    """

    _check_output = check_output

    def __init__(self, architecture: str, configuration: Configuration) -> None:
        """
        default constructor

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
        """
        self.logger = logging.getLogger("build_details")
        self.architecture = architecture
        self.configuration = configuration
        self.targets, self.default_key = self.sign_options(configuration)

    @property
    def repository_sign_args(self) -> List[str]:
        """
        get command line arguments based on settings

        Returns:
            List[str]: command line arguments for repo-add command to sign database
        """
        if SignSettings.Repository not in self.targets:
            return []
        if self.default_key is None:
            self.logger.error("no default key set, skip repository sign")
            return []
        return ["--sign", "--key", self.default_key]

    @staticmethod
    def sign_command(path: Path, key: str) -> List[str]:
        """
        gpg command to run

        Args:
            path(Path): path to file to sign
            key(str): PGP key ID

        Returns:
            List[str]: gpg command with all required arguments
        """
        return ["gpg", "-u", key, "-b", str(path)]

    @staticmethod
    def sign_options(configuration: Configuration) -> Tuple[Set[SignSettings], Optional[str]]:
        """
        extract default sign options from configuration

        Args:
            configuration(Configuration): configuration instance

        Returns:
            Tuple[Set[SignSettings], Optional[str]]: tuple of sign targets and default PGP key
        """
        targets: Set[SignSettings] = set()
        for option in configuration.getlist("sign", "target"):
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
            response = requests.get(f"http://{server}/pks/lookup", params={
                "op": "get",
                "options": "mr",
                "search": key
            })
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.logger.exception("could not download key %s from %s: %s", key, server, exception_response_text(e))
            raise
        return response.text

    def key_import(self, server: str, key: str) -> None:
        """
        import key to current user and sign it locally

        Args:
            server(str): public PGP server which will be used to download the key
            key(str): key ID to import
        """
        key_body = self.key_download(server, key)
        GPG._check_output("gpg", "--import", input_data=key_body, exception=None, logger=self.logger)

    def process(self, path: Path, key: str) -> List[Path]:
        """
        gpg command wrapper

        Args:
            path(Path): path to file to sign
            key(str): PGP key ID

        Returns:
            List[Path]: list of generated files including original file
        """
        GPG._check_output(
            *GPG.sign_command(path, key),
            exception=BuildFailed(path.name),
            logger=self.logger)
        return [path, path.parent / f"{path.name}.sig"]

    def process_sign_package(self, path: Path, base: str) -> List[Path]:
        """
        sign package if required by configuration

        Args:
            path(Path): path to file to sign
            base(str): package base required to check for key overrides

        Returns:
            List[Path]: list of generated files including original file
        """
        if SignSettings.Packages not in self.targets:
            return [path]
        key = self.configuration.get("sign", f"key_{base}", fallback=self.default_key)
        if key is None:
            self.logger.error("no default key set, skip package %s sign", path)
            return [path]
        return self.process(path, key)

    def process_sign_repository(self, path: Path) -> List[Path]:
        """
        sign repository if required by configuration
        :note: more likely you just want to pass `repository_sign_args` to repo wrapper

        Args:
            path(Path): path to repository database

        Returns:
            List[Path]: list of generated files including original file
        """
        if SignSettings.Repository not in self.targets:
            return [path]
        if self.default_key is None:
            self.logger.error("no default key set, skip repository sign")
            return [path]
        return self.process(path, self.default_key)
