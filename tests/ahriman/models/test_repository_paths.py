from pathlib import Path
from pytest_mock import MockerFixture
from unittest import mock

from ahriman.models.repository_paths import RepositoryPaths


def test_create_tree(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must create whole tree
    """
    paths = {
        prop
        for prop in dir(repository_paths)
        if not prop.startswith("_") and prop not in ("architecture", "create_tree", "root")
    }
    mocker.patch("pathlib.Path.mkdir")

    repository_paths.create_tree()
    Path.mkdir.assert_has_calls(
        [
            mock.call(mode=0o755, parents=True, exist_ok=True)
            for _ in paths
        ])
