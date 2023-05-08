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
    args.build_command = Path("/usr") / "bin" / "pkgctl"
    args.from_configuration = Path("/usr") / "local" / "share" / "devtools-git-poc" / "pacman.conf.d" / "extra.conf"
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
    init_mock = mocker.patch("ahriman.core.alpm.repo.Repo.init")

    Setup.run(args, "x86_64", configuration, report=False, unsafe=False)
    ahriman_configuration_mock.assert_called_once_with(args, "x86_64", args.repository, configuration)
    devtools_configuration_mock.assert_called_once_with(
        "x86_64", args.from_configuration, args.mirror, args.multilib, args.repository, repository_paths)
    makepkg_configuration_mock.assert_called_once_with(args.packager, args.makeflags_jobs, repository_paths)
    sudo_configuration_mock.assert_called_once_with(args.build_command)
    init_mock.assert_called_once_with()


def test_configuration_create_ahriman(args: argparse.Namespace, configuration: Configuration,
                                      repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must create configuration for the service
    """
    args = _default_args(args)
    mocker.patch("pathlib.Path.open")
    set_option_mock = mocker.patch("ahriman.core.configuration.Configuration.set_option")
    write_mock = mocker.patch("ahriman.core.configuration.Configuration.write")

    Setup.configuration_create_ahriman(args, "x86_64", args.repository, configuration)
    set_option_mock.assert_has_calls([
        MockCall("repository", "name", args.repository),
        MockCall(Configuration.section_name("build", "x86_64"), "build_command", str(args.build_command)),
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

    Setup.configuration_create_devtools("x86_64", args.from_configuration, None,
                                        args.multilib, args.repository, repository_paths)
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

    Setup.configuration_create_devtools("x86_64", args.from_configuration, args.mirror,
                                        False, args.repository, repository_paths)
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

    Setup.configuration_create_devtools("x86_64", args.from_configuration, None,
                                        False, args.repository, repository_paths)
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

    Setup.configuration_create_sudo(args.build_command)
    chmod_text_mock.assert_called_once_with(0o400)
    write_text_mock.assert_called_once_with(pytest.helpers.anyvar(str, True), encoding="utf8")


def test_disallow_auto_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Setup.ALLOW_AUTO_ARCHITECTURE_RUN
