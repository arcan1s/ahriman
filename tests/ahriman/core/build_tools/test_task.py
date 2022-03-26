from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.build_tools.task import Task
from ahriman.core.database.sqlite import SQLite


def test_build(task_ahriman: Task, mocker: MockerFixture) -> None:
    """
    must build package
    """
    check_output_mock = mocker.patch("ahriman.core.build_tools.task.Task._check_output")
    task_ahriman.build(Path("ahriman"))
    check_output_mock.assert_called()


def test_init_with_cache(task_ahriman: Task, database: SQLite, mocker: MockerFixture) -> None:
    """
    must copy tree instead of fetch
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("ahriman.core.build_tools.sources.Sources.load")
    copytree_mock = mocker.patch("shutil.copytree")

    task_ahriman.init(Path("ahriman"), database)
    copytree_mock.assert_called_once()  # we do not check full command here, sorry
