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
from importlib.metadata import Distribution, PackageNotFoundError

from tox.config.sets import EnvConfigSet
from tox.plugin import impl
from tox.session.state import State
from tox.tox_env.api import ToxEnv


def _extract_version(tox_env: ToxEnv) -> dict[str, str]:
    """
    extract version dynamically and set VERSION environment variable

    Args:
        tox_env(ToxEnv): tox environment containing the installed package

    Returns:
        dict[str, str]: environment variables which must be inserted

    Raises:
        PackageNotFoundError: no installed distribution has been found
    """
    distribution = tox_env.conf["dynamic_version"]
    if not distribution:
        return {}

    installed = next(
        (
            package for package in Distribution.discover(path=[str(tox_env.env_site_package_dir())])
            if package.name == distribution
        ),
        None,
    )
    if installed is None:
        raise PackageNotFoundError(distribution)

    return {"VERSION": installed.version}


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
        desc="distribution name used to populate the VERSION environment variable",
    )


@impl
def tox_before_run_commands(tox_env: ToxEnv) -> None:
    """
    called before the commands set is executed

    Args:
        tox_env(ToxEnv): the tox environment being executed
    """
    tox_env.conf["set_env"].update(_extract_version(tox_env))
