#
# copyright (c) 2021-2022 ahriman team.
#
# this file is part of ahriman
# (see https://github.com/arcan1s/ahriman).
#
# this program is free software: you can redistribute it and/or modify
# it under the terms of the gnu general public license as published by
# the free software foundation, either version 3 of the license, or
# (at your option) any later version.
#
# this program is distributed in the hope that it will be useful,
# but without any warranty; without even the implied warranty of
# merchantability or fitness for a particular purpose.  see the
# gnu general public license for more details.
#
# you should have received a copy of the gnu general public license
# along with this program. if not, see <http://www.gnu.org/licenses/>.
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
            runner = RemotePull(self.configuration, target)
            runner.run()
