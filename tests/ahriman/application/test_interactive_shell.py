import pytest

from pytest_mock import MockerFixture

from ahriman.application.interactive_shell import InteractiveShell


def test_interact(mocker: MockerFixture) -> None:
    """
    must call IPython shell
    """
    banner_mock = mocker.patch("IPython.terminal.embed.InteractiveShellEmbed.show_banner")
    interact_mock = mocker.patch("IPython.terminal.embed.InteractiveShellEmbed.interact")

    shell = InteractiveShell()
    shell.interact()
    banner_mock.assert_called_once_with()
    interact_mock.assert_called_once_with()


def test_interact_import_error(mocker: MockerFixture) -> None:
    """
    must call builtin shell if no IPython available
    """
    pytest.helpers.import_error("IPython.terminal.embed", ["InteractiveShellEmbed"], mocker)
    interact_mock = mocker.patch("code.InteractiveConsole.interact")

    shell = InteractiveShell()
    shell.interact()
    interact_mock.assert_called_once_with(shell)
