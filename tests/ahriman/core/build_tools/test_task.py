from pytest_mock import MockerFixture

from ahriman.core.build_tools.task import Task


def test_build(task_ahriman: Task, mocker: MockerFixture) -> None:
    """
    must build package
    """
    check_output_mock = mocker.patch("ahriman.core.build_tools.task.Task._check_output")
    task_ahriman.build()
    check_output_mock.assert_called()


def test_init_with_cache(task_ahriman: Task, mocker: MockerFixture) -> None:
    """
    must copy tree instead of fetch
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("ahriman.core.build_tools.sources.Sources.load")
    copytree_mock = mocker.patch("shutil.copytree")

    task_ahriman.init(None)
    copytree_mock.assert_called_once()
