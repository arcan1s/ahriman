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
from code import InteractiveConsole
from importlib.util import find_spec
from typing import Any


class InteractiveShell(InteractiveConsole):
    """
    wrapper around :class:`code.InteractiveConsole` to pass :func:`interact()` to IPython shell
    """

    @staticmethod
    def has_ipython() -> bool:
        """
        check if IPython shell is available

        Returns:
            bool: ``True`` if IPython shell is available, ``False`` otherwise
        """
        try:
            return find_spec("IPython.terminal.embed") is not None
        except ModuleNotFoundError:
            return False

    def interact(self, *args: Any, **kwargs: Any) -> None:
        """
        pass controller to IPython shell

        Args:
            *args(Any): positional arguments
            **kwargs(Any): keyword arguments
        """
        if self.has_ipython():
            from IPython.terminal.embed import InteractiveShellEmbed

            shell = InteractiveShellEmbed(user_ns=self.locals)  # type: ignore[no-untyped-call]
            shell.show_banner()  # type: ignore[no-untyped-call]
            shell.interact()  # type: ignore[no-untyped-call]
        else:
            # fallback to default
            import readline  # pylint: disable=unused-import
            InteractiveConsole.interact(self, *args, **kwargs)
