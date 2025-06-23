#
# Copyright (c) 2021-2025 ahriman team.
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
import importlib
import shlex
import sys

from tox.config.sets import EnvConfigSet
from tox.config.types import Command
from tox.plugin import impl
from tox.session.state import State
from tox.tox_env.api import ToxEnv


def _extract_version(env_conf: EnvConfigSet, python_path: str | None = None) -> dict[str, str]:
    """
    extract version dynamically and set VERSION environment variable

    Args:
        env_conf(EnvConfigSet): the core configuration object
        python_path(str | None): python path variable if available

    Returns:
        dict[str, str]: environment variables which must be inserted
    """
    import_path = env_conf["dynamic_version"]
    if not import_path:
        return {}

    if python_path is not None:
        sys.path.append(python_path)

    module_name, variable_name = import_path.rsplit(".", maxsplit=1)
    module = importlib.import_module(module_name)
    version = getattr(module, variable_name)

    # reset import paths
    sys.path.pop()

    return {"VERSION": version}


def _wrap_commands(env_conf: EnvConfigSet, shell: str = "bash") -> None:
    """
    wrap commands into shell if there is redirect

    Args:
        env_conf(EnvConfigSet): the core configuration object
        shell(str, optional): shell command to use (Default value = "bash")
    """
    if not env_conf["handle_redirect"]:
        return

    # append shell just in case
    env_conf["allowlist_externals"].append(shell)

    for command in env_conf["commands"]:
        if len(command.args) < 3:  # command itself, redirect and output
            continue

        redirect, output = command.args[-2:]
        if redirect not in (">", "2>", "&>"):
            continue

        command.args = [
            shell,
            "-c",
            f"{Command(command.args[:-2]).shell} {redirect} {shlex.quote(output)}",
        ]


@impl
def tox_add_env_config(env_conf: EnvConfigSet, state: State) -> None:
    """
    add a command line argument. This is the first hook to be called,
    right after the logging setup and config source discovery.

    Args:
        env_conf(EnvConfigSet): the core configuration object
        state(State): the global tox state object
    """
    del state

    env_conf.add_config(
        keys=["dynamic_version"],
        of_type=str,
        default="",
        desc="import path for the version variable",
    )
    env_conf.add_config(
        keys=["handle_redirect"],
        of_type=bool,
        default=False,
        desc="wrap commands to handle redirects if any",
    )


@impl
def tox_before_run_commands(tox_env: ToxEnv) -> None:
    """
    called before the commands set is executed

    Args:
        tox_env(ToxEnv): the tox environment being executed
    """
    env_conf = tox_env.conf
    set_env = env_conf["set_env"]

    python_path = set_env.load("PYTHONPATH") if "PYTHONPATH" in set_env else None
    set_env.update(_extract_version(env_conf, python_path))

    _wrap_commands(env_conf)
