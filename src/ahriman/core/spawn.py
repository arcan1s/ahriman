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
import time
import uuid

from collections.abc import Callable, Iterable
from multiprocessing import Process, Queue
from threading import Lock, Thread

from ahriman.core.log import LazyLogging


class Spawn(Thread, LazyLogging):
    """
    helper to spawn external ahriman process
    MUST NOT be used directly, the only one usage allowed is to spawn process from web services

    Attributes:
        active(dict[str, Process]): map of active child processes required to avoid zombies
        architecture(str): repository architecture
        command_arguments(list[str]): base command line arguments
        queue(Queue[tuple[str, bool, int]]): multiprocessing queue to read updates from processes
    """

    def __init__(self, args_parser: argparse.ArgumentParser, architecture: str, command_arguments: list[str]) -> None:
        """
        default constructor

        Args:
            args_parser(argparse.ArgumentParser): command line parser for the application
            architecture(str): repository architecture
            command_arguments(list[str]): base command line arguments
        """
        Thread.__init__(self, name="spawn")
        self.architecture = architecture

        self.args_parser = args_parser
        self.command_arguments = command_arguments

        self.lock = Lock()
        self.active: dict[str, Process] = {}
        # stupid pylint does not know that it is possible
        self.queue: Queue[tuple[str, bool, int] | None] = Queue()  # pylint: disable=unsubscriptable-object

    @staticmethod
    def boolean_action_argument(name: str, value: bool) -> str:
        """
        convert option of given name with value to boolean action argument

        Args:
            name(str): command line argument name
            value(bool): command line argument value

        Returns:
            str: if ``value`` is True, then returns positive flag and negative otherwise
        """
        return name if value else f"no-{name}"

    @staticmethod
    def process(callback: Callable[[argparse.Namespace, str], bool], args: argparse.Namespace, architecture: str,
                process_id: str, queue: Queue[tuple[str, bool, int]]) -> None:  # pylint: disable=unsubscriptable-object
        """
        helper to run external process

        Args:
            callback(Callable[[argparse.Namespace, str], bool]): application run function (i.e. Handler.run method)
            args(argparse.Namespace): command line arguments
            architecture(str): repository architecture
            process_id(str): process unique identifier
            queue(Queue[tuple[str, bool, int]]): output queue
        """
        start_time = time.monotonic()
        result = callback(args, architecture)
        stop_time = time.monotonic()

        consumed_time = int(1000 * (stop_time - start_time))

        queue.put((process_id, result, consumed_time))

    def _spawn_process(self, command: str, *args: str, **kwargs: str | None) -> str:
        """
        spawn external ahriman process with supplied arguments

        Args:
            command(str): subcommand to run
            *args(str): positional command arguments
            **kwargs(str): named command arguments

        Returns:
            str: spawned process id
        """
        # default arguments
        arguments = self.command_arguments[:]
        # positional command arguments
        arguments.append(command)
        arguments.extend(args)
        # named command arguments
        for argument, value in kwargs.items():
            if value is None:
                continue  # skip null values
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
        return process_id

    def has_process(self, process_id: str) -> bool:
        """
        check if given process is alive

        Args:
            process_id(str): process id to be checked as returned by ``Spawn._spawn_process``

        Returns:
            bool: True in case if process still counts as active and False otherwise
        """
        with self.lock:
            return process_id in self.active

    def key_import(self, key: str, server: str | None) -> str:
        """
        import key to service cache

        Args:
            key(str): key to import
            server(str | None): PGP key server

        Returns:
            str: spawned process id
        """
        kwargs = {} if server is None else {"key-server": server}
        return self._spawn_process("service-key-import", key, **kwargs)

    def packages_add(self, packages: Iterable[str], username: str | None, *, now: bool) -> str:
        """
        add packages

        Args:
            packages(Iterable[str]): packages list to add
            username(str | None): optional override of username for build process
            now(bool): build packages now

        Returns:
            str: spawned process id
        """
        kwargs = {"username": username}
        if now:
            kwargs["now"] = ""
        return self._spawn_process("package-add", *packages, **kwargs)

    def packages_rebuild(self, depends_on: str, username: str | None) -> str:
        """
        rebuild packages which depend on the specified package

        Args:
            depends_on(str): packages dependency
            username(str | None): optional override of username for build process

        Returns:
            str: spawned process id
        """
        kwargs = {"depends-on": depends_on, "username": username}
        return self._spawn_process("repo-rebuild", **kwargs)

    def packages_remove(self, packages: Iterable[str]) -> str:
        """
        remove packages

        Args:
            packages(Iterable[str]): packages list to remove

        Returns:
            str: spawned process id
        """
        return self._spawn_process("package-remove", *packages)

    def packages_update(self, username: str | None, *, aur: bool, local: bool, manual: bool) -> str:
        """
        run full repository update

        Args:
            username(str | None): optional override of username for build process
            aur(bool): check for aur updates
            local(bool): check for local packages updates
            manual(bool): check for manual packages

        Returns:
            str: spawned process id
        """
        kwargs = {
            "username": username,
            self.boolean_action_argument("aur", aur): "",
            self.boolean_action_argument("local", local): "",
            self.boolean_action_argument("manual", manual): "",
        }
        return self._spawn_process("repo-update", **kwargs)

    def run(self) -> None:
        """
        thread run method
        """
        for process_id, status, consumed_time in iter(self.queue.get, None):
            self.logger.info("process %s has been terminated with status %s, consumed time %s",
                             process_id, status, consumed_time / 1000)

            with self.lock:
                process = self.active.pop(process_id, None)

            if process is not None:
                process.join()

    def stop(self) -> None:
        """
        gracefully terminate thread
        """
        self.queue.put(None)
