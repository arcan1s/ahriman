import configparser
import os

from logging.config import fileConfig
from typing import Any, Dict, Optional

from ahriman.core.exceptions import MissingConfiguration


# built-in configparser extension
class Configuration(configparser.RawConfigParser):

    def __init__(self) -> None:
        configparser.RawConfigParser.__init__(self, allow_no_value=True)
        self.path = None  # type: Optional[str]

    @property
    def include(self) -> str:
        return self.get('settings', 'include')

    def get_section(self, section: str) -> Dict[str, str]:
        if not self.has_section(section):
            raise MissingConfiguration(section)
        return dict(self[section])

    def load(self, path: str) -> None:
        self.path = path
        self.read(self.path)
        self.load_includes()

    def load_includes(self) -> None:
        try:
            include_dir = self.include
            for conf in filter(lambda p: p.endswith('.ini'), sorted(os.listdir(include_dir))):
                self.read(os.path.join(self.include, conf))
        except (FileNotFoundError, configparser.NoOptionError):
            pass

    def load_logging(self) -> None:
        fileConfig(self.get('settings', 'logging'))
