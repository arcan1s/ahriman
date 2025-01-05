from pytest_mock import MockerFixture

from ahriman.application.interactive_shell import InteractiveShell


def test_has_ipython(mocker: MockerFixture) -> None:
    """
    must correctly check if IPython is installed
    """
    find_spec_mock = mocker.patch("ahriman.application.interactive_shell.find_spec")
    assert InteractiveShell.has_ipython()
    find_spec_mock.assert_called_once_with("IPython.terminal.embed")


def test_has_ipython_module_not_found(mocker: MockerFixture) -> None:
    """
    must return False if IPython is not installed
    """
    mocker.patch("ahriman.application.interactive_shell.find_spec", side_effect=ModuleNotFoundError)
    assert not InteractiveShell.has_ipython()


def test_interact(mocker: MockerFixture) -> None:
    """
    must call IPython shell
    """
    mocker.patch("ahriman.application.interactive_shell.InteractiveShell.has_ipython", return_value=True)
    banner_mock = mocker.patch("IPython.terminal.embed.InteractiveShellEmbed.show_banner")
    interact_mock = mocker.patch("IPython.terminal.embed.InteractiveShellEmbed.interact")

    shell = InteractiveShell()
    shell.interact()
    banner_mock.assert_called_once_with()
    interact_mock.assert_called_once_with()


def test_interact_no_ipython(mocker: MockerFixture) -> None:
    """
    must call builtin shell if no IPython available
    """
    mocker.patch("ahriman.application.interactive_shell.InteractiveShell.has_ipython", return_value=None)
    interact_mock = mocker.patch("code.InteractiveConsole.interact")

    shell = InteractiveShell()
    shell.interact()
    interact_mock.assert_called_once_with(shell)
