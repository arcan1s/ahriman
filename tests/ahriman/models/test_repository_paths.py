import os

from pytest_mock import MockerFixture
from unittest import mock

from ahriman.models.repository_paths import RepositoryPaths


def test_create_tree(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must create whole tree
    """
    paths = {
        property
        for property in dir(repository_paths)
        if not property.startswith("_") and property not in ("architecture", "create_tree", "root")
    }
    mocker.patch("os.makedirs")

    repository_paths.create_tree()
    os.makedirs.assert_has_calls(
        [
            mock.call(getattr(repository_paths, path), mode=0o755, exist_ok=True)
            for path in paths
        ], any_order=True)
