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
from ahriman.core.configuration import Configuration
from ahriman.core.gitremote.remote_pull import RemotePull
from ahriman.core.triggers import Trigger


class RemotePullTrigger(Trigger):
    """
    trigger based on pulling PKGBUILDs before the actions
    """

    def __init__(self, architecture: str, configuration: Configuration) -> None:
        """
        default constructor

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
        """
        Trigger.__init__(self, architecture, configuration)
        self.targets = configuration.getlist("remote-pull", "target", fallback=["gitremote"])

    def on_start(self) -> None:
        """
        trigger action which will be called at the start of the application
        """
        for target in self.targets:
            section, _ = self.configuration.gettype(target, self.architecture)
            runner = RemotePull(self.configuration, section)
            runner.run()
