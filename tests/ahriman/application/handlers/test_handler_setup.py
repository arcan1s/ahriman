import argparse
import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from typing import Any
from unittest.mock import call as MockCall

from ahriman.application.handlers import Setup
from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository
from ahriman.models.repository_paths import RepositoryPaths
from ahriman.models.sign_settings import SignSettings


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.build_as_user = "ahriman"
    args.build_command = "ahriman"
    args.from_configuration = Path("/usr/share/devtools/pacman-extra.conf")
    args.makeflags_jobs = True
    args.mirror = "mirror"
    args.multilib = True
    args.packager = "John Doe <john@doe.com>"
    args.repository = "aur-clone"
    args.sign_key = "key"
    args.sign_target = [SignSettings.Packages]
    args.web_port = 8080
    args.web_unix_socket = Path("/var/lib/ahriman/ahriman-web.sock")
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
             repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    ahriman_configuration_mock = mocker.patch("ahriman.application.handlers.Setup.configuration_create_ahriman")
    devtools_configuration_mock = mocker.patch("ahriman.application.handlers.Setup.configuration_create_devtools")
    makepkg_configuration_mock = mocker.patch("ahriman.application.handlers.Setup.configuration_create_makepkg")
    sudo_configuration_mock = mocker.patch("ahriman.application.handlers.Setup.configuration_create_sudo")
    executable_mock = mocker.patch("ahriman.application.handlers.Setup.executable_create")
    init_mock = mocker.patch("ahriman.core.alpm.repo.Repo.init")

    Setup.run(args, "x86_64", configuration, report=False, unsafe=False)
    ahriman_configuration_mock.assert_called_once_with(args, "x86_64", args.repository, configuration)
    devtools_configuration_mock.assert_called_once_with(
        args.build_command, "x86_64", args.from_configuration, args.mirror, args.multilib, args.repository,
        repository_paths)
    makepkg_configuration_mock.assert_called_once_with(args.packager, args.makeflags_jobs, repository_paths)
    sudo_configuration_mock.assert_called_once_with(repository_paths, args.build_command, "x86_64")
    executable_mock.assert_called_once_with(repository_paths, args.build_command, "x86_64")
    init_mock.assert_called_once_with()


def test_build_command(args: argparse.Namespace) -> None:
    """
    must generate correct build command name
    """
    args = _default_args(args)
    path = Path("local")

    build_command = Setup.build_command(path, args.build_command, "x86_64")
    assert build_command.name == f"{args.build_command}-x86_64-build"
    assert build_command.parent == path


def test_configuration_create_ahriman(args: argparse.Namespace, configuration: Configuration,
                                      repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must create configuration for the service
    """
    args = _default_args(args)
    mocker.patch("pathlib.Path.open")
    set_option_mock = mocker.patch("ahriman.core.configuration.Configuration.set_option")
    write_mock = mocker.patch("ahriman.core.configuration.Configuration.write")
    command = Setup.build_command(repository_paths.root, args.build_command, "x86_64")

    Setup.configuration_create_ahriman(args, "x86_64", args.repository, configuration)
    set_option_mock.assert_has_calls([
        MockCall(Configuration.section_name("build", "x86_64"), "build_command", str(command)),
        MockCall("repository", "name", args.repository),
        MockCall(Configuration.section_name("build", "x86_64"), "makechrootpkg_flags", f"-U {args.build_as_user}"),
        MockCall(Configuration.section_name("alpm", "x86_64"), "mirror", args.mirror),
        MockCall(Configuration.section_name("sign", "x86_64"), "target",
                 " ".join([target.name.lower() for target in args.sign_target])),
        MockCall(Configuration.section_name("sign", "x86_64"), "key", args.sign_key),
        MockCall(Configuration.section_name("web", "x86_64"), "port", str(args.web_port)),
        MockCall(Configuration.section_name("web", "x86_64"), "unix_socket", str(args.web_unix_socket)),
    ])
    write_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_configuration_create_ahriman_no_multilib(args: argparse.Namespace, configuration: Configuration,
                                                  repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must create configuration for the service without multilib repository
    """
    args = _default_args(args)
    args.multilib = False
    mocker.patch("pathlib.Path.open")
    mocker.patch("ahriman.core.configuration.Configuration.write")
    set_option_mock = mocker.patch("ahriman.core.configuration.Configuration.set_option")

    Setup.configuration_create_ahriman(args, "x86_64", args.repository, configuration)
    set_option_mock.assert_has_calls([
        MockCall(Configuration.section_name("alpm", "x86_64"), "mirror", args.mirror),
    ])  # non-strict check called intentionally


def test_configuration_create_devtools(args: argparse.Namespace, repository_paths: RepositoryPaths,
                                       mocker: MockerFixture) -> None:
    """
    must create configuration for the devtools
    """
    args = _default_args(args)
    mocker.patch("pathlib.Path.open")
    mocker.patch("ahriman.core.configuration.Configuration.set")
    add_section_mock = mocker.patch("ahriman.core.configuration.Configuration.add_section")
    write_mock = mocker.patch("ahriman.core.configuration.Configuration.write")

    Setup.configuration_create_devtools(args.build_command, "x86_64", args.from_configuration,
                                        None, args.multilib, args.repository, repository_paths)
    add_section_mock.assert_has_calls([MockCall("multilib"), MockCall(args.repository)])
    write_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_configuration_create_devtools_mirror(args: argparse.Namespace, repository_paths: RepositoryPaths,
                                              mocker: MockerFixture) -> None:
    """
    must create configuration for the devtools with mirror set explicitly
    """
    def get(section: str, key: str, **kwargs: Any) -> Any:
        if section == "core" and key == "Include":
            return str(Setup.MIRRORLIST_PATH)
        return kwargs["fallback"]

    args = _default_args(args)
    mocker.patch("pathlib.Path.open")
    mocker.patch("ahriman.core.configuration.Configuration.set")
    mocker.patch("ahriman.core.configuration.Configuration.write")
    mocker.patch("ahriman.core.configuration.Configuration.sections", return_value=["core", "extra"])
    get_mock = mocker.patch("ahriman.core.configuration.Configuration.get", side_effect=get)
    remove_option_mock = mocker.patch("ahriman.core.configuration.Configuration.remove_option")
    set_option_mock = mocker.patch("ahriman.core.configuration.Configuration.set_option")

    Setup.configuration_create_devtools(args.build_command, "x86_64", args.from_configuration,
                                        args.mirror, False, args.repository, repository_paths)
    get_mock.assert_has_calls([MockCall("core", "Include", fallback=None), MockCall("extra", "Include", fallback=None)])
    remove_option_mock.assert_called_once_with("core", "Include")
    set_option_mock.assert_has_calls([MockCall("core", "Server", args.mirror)])  # non-strict check called intentionally


def test_configuration_create_devtools_no_multilib(args: argparse.Namespace, repository_paths: RepositoryPaths,
                                                   mocker: MockerFixture) -> None:
    """
    must create configuration for the devtools without multilib
    """
    args = _default_args(args)
    mocker.patch("pathlib.Path.open")
    mocker.patch("ahriman.core.configuration.Configuration.set")
    write_mock = mocker.patch("ahriman.core.configuration.Configuration.write")

    Setup.configuration_create_devtools(args.build_command, "x86_64", args.from_configuration,
                                        None, False, args.repository, repository_paths)
    write_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_configuration_create_makepkg(args: argparse.Namespace, repository_paths: RepositoryPaths,
                                      passwd: Any, mocker: MockerFixture) -> None:
    """
    must create makepkg configuration
    """
    args = _default_args(args)
    mocker.patch("ahriman.application.handlers.setup.getpwuid", return_value=passwd)
    write_text_mock = mocker.patch("pathlib.Path.write_text", autospec=True)

    Setup.configuration_create_makepkg(args.packager, args.makeflags_jobs, repository_paths)
    write_text_mock.assert_called_once_with(
        Path("home") / ".makepkg.conf", pytest.helpers.anyvar(str, True), encoding="utf8")


def test_configuration_create_sudo(args: argparse.Namespace, repository_paths: RepositoryPaths,
                                   mocker: MockerFixture) -> None:
    """
    must create sudo configuration
    """
    args = _default_args(args)
    chmod_text_mock = mocker.patch("pathlib.Path.chmod")
    write_text_mock = mocker.patch("pathlib.Path.write_text")

    Setup.configuration_create_sudo(repository_paths, args.build_command, "x86_64")
    chmod_text_mock.assert_called_once_with(0o400)
    write_text_mock.assert_called_once_with(pytest.helpers.anyvar(str, True), encoding="utf8")


def test_executable_create(args: argparse.Namespace, repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must create executable
    """
    args = _default_args(args)
    chown_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.chown")
    symlink_mock = mocker.patch("pathlib.Path.symlink_to")
    unlink_mock = mocker.patch("pathlib.Path.unlink")

    Setup.executable_create(repository_paths, args.build_command, "x86_64")
    chown_mock.assert_called_once_with(Setup.build_command(repository_paths.root, args.build_command, "x86_64"))
    symlink_mock.assert_called_once_with(Setup.ARCHBUILD_COMMAND_PATH)
    unlink_mock.assert_called_once_with(missing_ok=True)


def test_disallow_auto_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Setup.ALLOW_AUTO_ARCHITECTURE_RUN
