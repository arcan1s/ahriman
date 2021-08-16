#
# Copyright (c) 2021 ahriman team.
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
    :ivar architecture: repository architecture
    :ivar configuration: configuration instance
    :ivar default_key: default PGP key ID to use
    :ivar logger: class logger
    :ivar targets: list of targets to sign (repository, package etc)
    """

    _check_output = check_output

    def __init__(self, architecture: str, configuration: Configuration) -> None:
        """
        default constructor
        :param architecture: repository architecture
        :param configuration: configuration instance
        """
        self.logger = logging.getLogger("build_details")
        self.architecture = architecture
        self.configuration = configuration
        self.targets, self.default_key = self.sign_options(configuration)

    @property
    def repository_sign_args(self) -> List[str]:
        """
        :return: command line arguments for repo-add command to sign database
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
        :param path: path to file to sign
        :param key: PGP key ID
        :return: gpg command with all required arguments
        """
        return ["gpg", "-u", key, "-b", str(path)]

    @staticmethod
    def sign_options(configuration: Configuration) -> Tuple[Set[SignSettings], Optional[str]]:
        """
        extract default sign options from configuration
        :param configuration: configuration instance
        :return: tuple of sign targets and default PGP key
        """
        targets = {
            SignSettings.from_option(option)
            for option in configuration.getlist("sign", "target")
        }
        default_key = configuration.get("sign", "key") if targets else None
        return targets, default_key

    def download_key(self, server: str, key: str) -> str:
        """
        download key from public PGP server
        :param server: public PGP server which will be used to download the key
        :param key: key ID to download
        :return: key as plain text
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

    def import_key(self, server: str, key: str) -> None:
        """
        import key to current user and sign it locally
        :param server: public PGP server which will be used to download the key
        :param key: key ID to import
        """
        key_body = self.download_key(server, key)
        GPG._check_output("gpg", "--import", input_data=key_body, exception=None, logger=self.logger)
        GPG._check_output("gpg", "--quick-lsign-key", key, exception=None, logger=self.logger)

    def process(self, path: Path, key: str) -> List[Path]:
        """
        gpg command wrapper
        :param path: path to file to sign
        :param key: PGP key ID
        :return: list of generated files including original file
        """
        GPG._check_output(
            *GPG.sign_command(path, key),
            exception=BuildFailed(path.name),
            logger=self.logger)
        return [path, path.parent / f"{path.name}.sig"]

    def sign_package(self, path: Path, base: str) -> List[Path]:
        """
        sign package if required by configuration
        :param path: path to file to sign
        :param base: package base required to check for key overrides
        :return: list of generated files including original file
        """
        if SignSettings.Packages not in self.targets:
            return [path]
        key = self.configuration.get("sign", f"key_{base}", fallback=self.default_key)
        if key is None:
            self.logger.error("no default key set, skip package %s sign", path)
            return [path]
        return self.process(path, key)

    def sign_repository(self, path: Path) -> List[Path]:
        """
        sign repository if required by configuration
        :note: more likely you just want to pass `repository_sign_args` to repo wrapper
        :param path: path to repository database
        :return: list of generated files including original file
        """
        if SignSettings.Repository not in self.targets:
            return [path]
        if self.default_key is None:
            self.logger.error("no default key set, skip repository sign")
            return [path]
        return self.process(path, self.default_key)
