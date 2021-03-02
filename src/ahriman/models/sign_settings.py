from __future__ import annotations

from enum import Enum, auto
from typing import Type

from ahriman.core.exceptions import InvalidOptionException


class SignSettings(Enum):
    Disabled = auto()
    SignPackages = auto()
    SignRepository = auto()

    @classmethod
    def from_option(cls: Type[SignSettings], value: str) -> SignSettings:
        if value.lower() in ('no', 'disabled'):
            return cls.Disabled
        elif value.lower() in ('package', 'packages', 'sign-package'):
            return cls.SignPackages
        elif value.lower() in ('repository', 'sign-repository'):
            return cls.SignRepository
        raise InvalidOptionException(value)