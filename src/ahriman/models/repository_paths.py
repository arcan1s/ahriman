import os

from dataclasses import dataclass


@dataclass
class RepositoryPaths:
    root: str

    @property
    def chroot(self) -> str:
        return os.path.join(self.root, 'chroot')

    @property
    def manual(self) -> str:
        return os.path.join(self.root, 'manual')

    @property
    def packages(self) -> str:
        return os.path.join(self.root, 'packages')

    @property
    def repository(self) -> str:
        return os.path.join(self.root, 'repository')

    @property
    def sources(self) -> str:
        return os.path.join(self.root, 'sources')

    def create_tree(self) -> None:
        os.makedirs(self.chroot, mode=0o755, exist_ok=True)
        os.makedirs(self.manual, mode=0o755, exist_ok=True)
        os.makedirs(self.packages, mode=0o755, exist_ok=True)
        os.makedirs(self.repository, mode=0o755, exist_ok=True)
        os.makedirs(self.sources, mode=0o755, exist_ok=True)