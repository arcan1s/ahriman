import pytest

from typing import Any, Type, TypeVar

T = TypeVar("T")


# https://stackoverflow.com/a/21611963
@pytest.helpers.register
def anyvar(cls: Type[T], strict: bool = False) -> T:
    class AnyVar(cls):
        def __eq__(self, other: Any) -> bool:
            return not strict or isinstance(other, cls)
    return AnyVar()
