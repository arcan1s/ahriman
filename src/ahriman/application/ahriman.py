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
import argparse

from pathlib import Path

import ahriman.application.handlers

from ahriman import __version__
from ahriman.application.handlers.handler import Handler
from ahriman.application.help_formatter import _HelpFormatter
from ahriman.core.module_loader import implementations
from ahriman.core.utils import enum_values
from ahriman.models.log_handler import LogHandler


__all__: list[str] = []


def _parser() -> argparse.ArgumentParser:
    """
    command line parser generator

    Returns:
        argparse.ArgumentParser: command line parser for the application
    """
    parser = argparse.ArgumentParser(prog="ahriman", description="ArcH linux ReposItory MANager",
                                     epilog="""
Quick setup command (replace repository name, architecture and packager as needed):

>>> ahriman -a x86_64 -r aur service-setup --packager "ahriman bot <ahriman@example.com>"

Add new package from AUR:

>>> ahriman package-add ahriman --now

Check for updates and build out-of-dated packages (add ``--dry-run`` to build it later):

>>> ahriman repo-update

Remove package from the repository:

>>> ahriman package-remove ahriman

Start web service (requires additional configuration):

>>> ahriman web
""",
                                     fromfile_prefix_chars="@", formatter_class=_HelpFormatter)
    parser.add_argument("-a", "--architecture", help="filter by target architecture")
    parser.add_argument("-c", "--configuration", help="configuration path", type=Path,
                        default=Path("/") / "etc" / "ahriman.ini")
    parser.add_argument("--force", help="force run, remove file lock", action="store_true")
    parser.add_argument("-l", "--lock", help="lock file", type=Path, default=Path("ahriman.pid"))
    parser.add_argument("--log-handler", help="explicit log handler specification. If none set, the handler will be "
                                              "guessed from environment",
                        type=LogHandler, choices=enum_values(LogHandler))
    parser.add_argument("-q", "--quiet", help="force disable any logging", action="store_true")
    parser.add_argument("--report", help="force enable or disable reporting to web service",
                        action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("-r", "--repository", help="filter by target repository")
    # special secret argument for systemd unit. The issue is that systemd doesn't allow multiple arguments to template
    # name. This parameter accepts [[arch]-repo] in order to keep backward compatibility
    parser.add_argument("--repository-id", help=argparse.SUPPRESS)
    parser.add_argument("--unsafe", help="allow to run ahriman as non-ahriman user. Some actions might be unavailable",
                        action="store_true")
    parser.add_argument("-V", "--version", action="version", version=__version__)
    parser.add_argument("--wait-timeout", help="wait for lock to be free. Negative value will lead to "
                                               "immediate application run even if there is lock file. "
                                               "In case of zero value, the application will wait infinitely",
                        type=int, default=-1)

    subparsers = parser.add_subparsers(title="command", help="command to run", dest="command")

    for handler in implementations(ahriman.application.handlers, Handler):
        for subparser_parser in handler.arguments:
            subparser = subparser_parser(subparsers)
            subparser.formatter_class = _HelpFormatter
            subparser.set_defaults(handler=handler, parser=_parser)

    # sort actions alphabetically in both choices and help message
    # pylint: disable=protected-access
    subparsers._choices_actions = sorted(subparsers._choices_actions, key=lambda action: action.dest)
    subparsers.choices = dict(sorted(subparsers.choices.items()))

    return parser


def run() -> int:
    """
    run application instance

    Returns:
        int: application status code
    """
    parser = _parser()
    args = parser.parse_args()

    if args.command is None:  # in case of empty command we would like to print help message
        parser.exit(status=2, message=parser.format_help())

    handler: Handler = args.handler
    return handler.execute(args)
