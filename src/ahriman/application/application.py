import os

from typing import List

from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository
from ahriman.core.task import Task
from ahriman.models.package import Package


class Application:

    def __init__(self, config: Configuration) -> None:
        self.config = config
        self.repository = Repository(config)

    def add(self, names: List[str]) -> None:
        for name in names:
            package = Package.load(name, self.config.get('aur', 'url'))
            task = Task(package, self.config, self.repository.paths)
            task.fetch(os.path.join(self.repository.paths.manual, package.name))

    def remove(self, names: List[str]) -> None:
        self.repository.process_remove(names)

    def update(self) -> None:
        updates = self.repository.updates()
        packages = self.repository.process_build(updates)
        self.repository.process_update(packages)