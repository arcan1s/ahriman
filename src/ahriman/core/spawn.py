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
from __future__ import annotations

import argparse
import uuid

from multiprocessing import Process, Queue
from threading import Lock, Thread
from typing import Callable, Dict, Iterable, Optional, Tuple

from ahriman.core.configuration import Configuration
from ahriman.core.log import LazyLogging
from ahriman.models.package_source import PackageSource


class Spawn(Thread, LazyLogging):
    """
    helper to spawn external ahriman process
    MUST NOT be used directly, the only one usage allowed is to spawn process from web services

    Attributes:
        active(Dict[str, Process]): map of active child processes required to avoid zombies
        architecture(str): repository architecture
        configuration(Configuration): configuration instance
        queue(Queue[Tuple[str, bool]]): multiprocessing queue to read updates from processes
    """

    def __init__(self, args_parser: argparse.ArgumentParser, architecture: str, configuration: Configuration) -> None:
        """
        default constructor

        Args:
            args_parser(argparse.ArgumentParser): command line parser for the application
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
        """
        Thread.__init__(self, name="spawn")
        self.architecture = architecture
        self.args_parser = args_parser
        self.configuration = configuration

        self.lock = Lock()
        self.active: Dict[str, Process] = {}
        # stupid pylint does not know that it is possible
        self.queue: Queue[Tuple[str, bool] | None] = Queue()  # pylint: disable=unsubscriptable-object

    @staticmethod
    def process(callback: Callable[[argparse.Namespace, str], bool], args: argparse.Namespace, architecture: str,
                process_id: str, queue: Queue[Tuple[str, bool]]) -> None:  # pylint: disable=unsubscriptable-object
        """
        helper to run external process

        Args:
            callback(Callable[[argparse.Namespace, str], bool]): application run function (i.e. Handler.run method)
            args(argparse.Namespace): command line arguments
            architecture(str): repository architecture
            process_id(str): process unique identifier
            queue(Queue[Tuple[str, bool]]): output queue
        """
        result = callback(args, architecture)
        queue.put((process_id, result))

    def _spawn_process(self, command: str, *args: str, **kwargs: str) -> None:
        """
        spawn external ahriman process with supplied arguments

        Args:
            command(str): subcommand to run
            *args(str): positional command arguments
            **kwargs(str): named command arguments
        """
        # default arguments
        arguments = ["--architecture", self.architecture]
        if self.configuration.path is not None:
            arguments.extend(["--configuration", str(self.configuration.path)])
        # positional command arguments
        arguments.append(command)
        arguments.extend(args)
        # named command arguments
        for argument, value in kwargs.items():
            arguments.append(f"--{argument}")
            if value:
                arguments.append(value)

        process_id = str(uuid.uuid4())
        self.logger.info("full command line arguments of %s are %s", process_id, arguments)
        parsed = self.args_parser.parse_args(arguments)

        callback = parsed.handler.call
        process = Process(target=self.process,
                          args=(callback, parsed, self.architecture, process_id, self.queue),
                          daemon=True)
        process.start()

        with self.lock:
            self.active[process_id] = process

    def key_import(self, key: str, server: Optional[str]) -> None:
        """
        import key to service cache

        Args:
            key(str): key to import
            server(str): PGP key server
        """
        kwargs = {} if server is None else {"key-server": server}
        self._spawn_process("service-key-import", key, **kwargs)

    def packages_add(self, packages: Iterable[str], *, now: bool) -> None:
        """
        add packages

        Args:
            packages(Iterable[str]): packages list to add
            now(bool): build packages now
        """
        kwargs = {"source": PackageSource.AUR.value}  # avoid abusing by building non-aur packages
        if now:
            kwargs["now"] = ""
        self._spawn_process("package-add", *packages, **kwargs)

    def packages_rebuild(self, depends_on: str) -> None:
        """
        rebuild packages which depend on the specified package

        Args:
            depends_on(str): packages dependency
        """
        self._spawn_process("repo-rebuild", **{"depends-on": depends_on})

    def packages_remove(self, packages: Iterable[str]) -> None:
        """
        remove packages

        Args:
            packages(Iterable[str]): packages list to remove
        """
        self._spawn_process("package-remove", *packages)

    def packages_update(self, ) -> None:
        """
        run full repository update
        """
        self._spawn_process("repo-update")

    def run(self) -> None:
        """
        thread run method
        """
        for process_id, status in iter(self.queue.get, None):
            self.logger.info("process %s has been terminated with status %s", process_id, status)

            with self.lock:
                process = self.active.pop(process_id, None)

            if process is not None:
                process.terminate()  # make sure lol
                process.join()

    def stop(self) -> None:
        """
        gracefully terminate thread
        """
        self.queue.put(None)
