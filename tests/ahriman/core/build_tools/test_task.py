from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.build_tools.task import Task
from ahriman.core.database import SQLite


def test_build(task_ahriman: Task, mocker: MockerFixture) -> None:
    """
    must build package
    """
    check_output_mock = mocker.patch("ahriman.core.build_tools.task.Task._check_output")
    task_ahriman.build(Path("ahriman"))
    check_output_mock.assert_called()


def test_init(task_ahriman: Task, database: SQLite, mocker: MockerFixture) -> None:
    """
    must copy tree instead of fetch
    """
    load_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.load")
    task_ahriman.init(Path("ahriman"), database)
    load_mock.assert_called_once_with(Path("ahriman"), task_ahriman.package, None, task_ahriman.paths)
