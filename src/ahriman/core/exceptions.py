from typing import Any


class BuildFailed(Exception):
    def __init__(self, package: str) -> None:
        Exception.__init__(self, f'Package {package} build failed, check logs for details')


class InvalidOptionException(Exception):
    def __init__(self, value: Any) -> None:
        Exception.__init__(self, f'Invalid or unknown option value `{value}`')


class InvalidPackageInfo(Exception):
    def __init__(self, details: Any) -> None:
        Exception.__init__(self, f'There are errors during reading package information: `{details}`')


class MissingConfiguration(Exception):
    def __init__(self, name: str) -> None:
        Exception.__init__(self, f'No section `{name}` found')
