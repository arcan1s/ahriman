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
from __future__ import annotations

import argparse
import logging
import uuid

from multiprocessing import Process, Queue
from threading import Lock, Thread
from typing import Callable, Dict, Iterable, Tuple

from ahriman.core.configuration import Configuration


class Spawn(Thread):
    """
    helper to spawn external ahriman process
    MUST NOT be used directly, the only one usage allowed is to spawn process from web services
    :ivar active: map of active child processes required to avoid zombies
    :ivar architecture: repository architecture
    :ivar configuration: configuration instance
    :ivar logger: spawner logger
    :ivar queue: multiprocessing queue to read updates from processes
    """

    def __init__(self, args_parser: argparse.ArgumentParser, architecture: str, configuration: Configuration) -> None:
        """
        default constructor
        :param args_parser: command line parser for the application
        :param architecture: repository architecture
        :param configuration: configuration instance
        """
        Thread.__init__(self, name="spawn")
        self.architecture = architecture
        self.args_parser = args_parser
        self.configuration = configuration
        self.logger = logging.getLogger("http")

        self.lock = Lock()
        self.active: Dict[str, Process] = {}
        # stupid pylint does not know that it is possible
        self.queue: Queue[Tuple[str, bool]] = Queue()  # pylint: disable=unsubscriptable-object

    @staticmethod
    def process(callback: Callable[[argparse.Namespace, str], bool], args: argparse.Namespace, architecture: str,
                process_id: str, queue: Queue[Tuple[str, bool]]) -> None:  # pylint: disable=unsubscriptable-object
        """
        helper to run external process
        :param callback: application run function (i.e. Handler.run method)
        :param args: command line arguments
        :param architecture: repository architecture
        :param process_id: process unique identifier
        :param queue: output queue
        """
        result = callback(args, architecture)
        queue.put((process_id, result))

    def packages_add(self, packages: Iterable[str], now: bool) -> None:
        """
        add packages
        :param packages: packages list to add
        :param now: build packages now
        """
        kwargs = {"now": ""} if now else {}
        self.spawn_process("add", *packages, **kwargs)

    def packages_remove(self, packages: Iterable[str]) -> None:
        """
        remove packages
        :param packages: packages list to remove
        """
        self.spawn_process("remove", *packages)

    def spawn_process(self, command: str, *args: str, **kwargs: str) -> None:
        """
        spawn external ahriman process with supplied arguments
        :param command: subcommand to run
        :param args: positional command arguments
        :param kwargs: named command arguments
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
