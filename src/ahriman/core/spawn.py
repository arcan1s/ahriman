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
from __future__ import annotations

import argparse
import uuid

from collections.abc import Callable, Iterable
from multiprocessing import Process, Queue
from threading import Lock, Thread

from ahriman.core.log import LazyLogging
from ahriman.models.metrics_timer import MetricsTimer
from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.process_status import ProcessStatus
from ahriman.models.repository_id import RepositoryId


class Spawn(Thread, LazyLogging):
    """
    helper to spawn external ahriman process
    MUST NOT be used directly, the only one usage allowed is to spawn process from web services

    Attributes:
        active(dict[str, Process]): map of active child processes required to avoid zombies
        command_arguments(list[str]): base command line arguments
        queue(Queue[ProcessStatus | None]): multiprocessing queue to read updates from processes
    """

    def __init__(self, args_parser: argparse.ArgumentParser, command_arguments: list[str]) -> None:
        """
        Args:
            args_parser(argparse.ArgumentParser): command line parser for the application
            command_arguments(list[str]): base command line arguments
        """
        Thread.__init__(self, name="spawn")

        self.args_parser = args_parser
        self.command_arguments = command_arguments

        self._lock = Lock()
        self.active: dict[str, Process] = {}
        # stupid pylint does not know that it is possible
        self.queue: Queue[ProcessStatus | None] = Queue()  # pylint: disable=unsubscriptable-object

    @staticmethod
    def boolean_action_argument(name: str, value: bool) -> str:
        """
        convert option of given name with value to boolean action argument

        Args:
            name(str): command line argument name
            value(bool): command line argument value

        Returns:
            str: if ``value`` is ``True``, then returns positive flag and negative otherwise
        """
        return name if value else f"no-{name}"

    @staticmethod
    def process(callback: Callable[[argparse.Namespace, RepositoryId], bool], args: argparse.Namespace,
                repository_id: RepositoryId, process_id: str, queue: Queue[ProcessStatus | None]) -> None:  # pylint: disable=unsubscriptable-object
        """
        helper to run external process

        Args:
            callback(Callable[[argparse.Namespace, str], bool]): application run function
                (i.e. :func:`ahriman.application.handlers.handler.Handler.call()` method)
            args(argparse.Namespace): command line arguments
            repository_id(RepositoryId): repository unique identifier
            process_id(str): process unique identifier
            queue(Queue[ProcessStatus | None]): output queue
        """
        with MetricsTimer() as timer:
            result = callback(args, repository_id)
            consumed_time = timer.elapsed

        queue.put(ProcessStatus(process_id, result, consumed_time))

    def _spawn_process(self, repository_id: RepositoryId, command: str, *args: str,
                       **kwargs: str | list[str] | None) -> str:
        """
        spawn external ahriman process with supplied arguments

        Args:
            repository_id(RepositoryId): repository unique identifier
            command(str): subcommand to run
            *args(str): positional command arguments
            **kwargs(str | list[str] | None): named command arguments

        Returns:
            str: spawned process identifier
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
            flag = f"--{argument}"
            if isinstance(value, list):
                arguments.extend(list(sum(((flag, v) for v in value), ())))
            elif value:
                arguments.extend([flag, value])
            else:
                arguments.append(flag)  # boolean argument

        process_id = str(uuid.uuid4())
        self.logger.info("full command line arguments of %s are %s using repository %s",
                         process_id, arguments, repository_id)

        parsed = self.args_parser.parse_args(arguments)

        callback = parsed.handler.call
        process = Process(target=self.process,
                          args=(callback, parsed, repository_id, process_id, self.queue),
                          daemon=True)
        process.start()

        with self._lock:
            self.active[process_id] = process
        return process_id

    def has_process(self, process_id: str) -> bool:
        """
        check if given process is alive

        Args:
            process_id(str): process id to be checked as returned by :func:`_spawn_process()`

        Returns:
            bool: ``True`` in case if process still counts as active and ``False`` otherwise
        """
        with self._lock:
            return process_id in self.active

    def key_import(self, key: str, server: str | None) -> str:
        """
        import key to service cache

        Args:
            key(str): key to import
            server(str | None): PGP key server

        Returns:
            str: spawned process identifier
        """
        kwargs = {} if server is None else {"key-server": server}
        repository_id = RepositoryId("", "")
        return self._spawn_process(repository_id, "service-key-import", key, **kwargs)

    def packages_add(self, repository_id: RepositoryId, packages: Iterable[str], username: str | None, *,
                     patches: list[PkgbuildPatch], now: bool, increment: bool, refresh: bool) -> str:
        """
        add packages

        Args:
            repository_id(RepositoryId): repository unique identifier
            packages(Iterable[str]): packages list to add
            username(str | None): optional override of username for build process
            patches(list[PkgbuildPatch]): list of patches to be passed
            now(bool): build packages now
            increment(bool): increment pkgrel on conflict
            refresh(bool): refresh pacman database before process

        Returns:
            str: spawned process identifier
        """
        kwargs: dict[str, str | list[str] | None] = {
            "username": username,
            "variable": [patch.serialize() for patch in patches],
            self.boolean_action_argument("increment", increment): "",
        }
        if now:
            kwargs["now"] = ""
        if refresh:
            kwargs["refresh"] = ""

        return self._spawn_process(repository_id, "package-add", *packages, **kwargs)

    def packages_rebuild(self, repository_id: RepositoryId, depends_on: str, username: str | None, *,
                         increment: bool) -> str:
        """
        rebuild packages which depend on the specified package

        Args:
            repository_id(RepositoryId): repository unique identifier
            depends_on(str): packages dependency
            username(str | None): optional override of username for build process
            increment(bool): increment pkgrel on conflict

        Returns:
            str: spawned process identifier
        """
        kwargs = {
            "depends-on": depends_on,
            "username": username,
            self.boolean_action_argument("increment", increment): "",
        }
        return self._spawn_process(repository_id, "repo-rebuild", **kwargs)

    def packages_remove(self, repository_id: RepositoryId, packages: Iterable[str]) -> str:
        """
        remove packages

        Args:
            repository_id(RepositoryId): repository unique identifier
            packages(Iterable[str]): packages list to remove

        Returns:
            str: spawned process identifier
        """
        return self._spawn_process(repository_id, "package-remove", *packages)

    def packages_update(self, repository_id: RepositoryId, username: str | None, *,
                        aur: bool, local: bool, manual: bool, increment: bool, refresh: bool) -> str:
        """
        run full repository update

        Args:
            repository_id(RepositoryId): repository unique identifier
            username(str | None): optional override of username for build process
            aur(bool): check for aur updates
            local(bool): check for local packages updates
            manual(bool): check for manual packages
            increment(bool): increment pkgrel on conflict
            refresh(bool): refresh pacman database before process

        Returns:
            str: spawned process identifier
        """
        kwargs = {
            "username": username,
            self.boolean_action_argument("aur", aur): "",
            self.boolean_action_argument("local", local): "",
            self.boolean_action_argument("manual", manual): "",
            self.boolean_action_argument("increment", increment): "",
        }
        if refresh:
            kwargs["refresh"] = ""

        return self._spawn_process(repository_id, "repo-update", **kwargs)

    def run(self) -> None:
        """
        thread run method
        """
        for terminated in iter(self.queue.get, None):
            self.logger.info("process %s has been terminated with status %s, consumed time %ss",
                             terminated.process_id, terminated.status, terminated.consumed_time)

            with self._lock:
                process = self.active.pop(terminated.process_id, None)

            if process is not None:
                process.join()

    def stop(self) -> None:
        """
        gracefully terminate thread
        """
        self.queue.put(None)
