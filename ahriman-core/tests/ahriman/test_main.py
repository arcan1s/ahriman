import runpy

from pytest_mock import MockerFixture


def test_main(mocker: MockerFixture) -> None:
    """
    must run the application and exit with its status
    """
    run = mocker.patch("ahriman.application.ahriman.run", return_value=42)
    exit_mock = mocker.patch("sys.exit")

    runpy.run_module("ahriman", run_name="__main__")
    run.assert_called_once_with()
    exit_mock.assert_called_once_with(42)
