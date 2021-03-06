import argparse

from pathlib import Path
from pytest_mock import MockerFixture
from unittest import mock

from ahriman.application.handlers import Setup
from ahriman.core.configuration import Configuration
from ahriman.models.repository_paths import RepositoryPaths
from ahriman.models.sign_settings import SignSettings


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    args.build_command = "ahriman"
    args.from_configuration = Path("/usr/share/devtools/pacman-extra.conf")
    args.no_multilib = False
    args.packager = "John Doe <john@doe.com>"
    args.repository = "aur-clone"
    args.sign_key = "key"
    args.sign_target = [SignSettings.Packages]
    args.web_port = 8080
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("pathlib.Path.mkdir")
    ahriman_configuration_mock = mocker.patch("ahriman.application.handlers.setup.Setup.create_ahriman_configuration")
    devtools_configuration_mock = mocker.patch("ahriman.application.handlers.setup.Setup.create_devtools_configuration")
    makepkg_configuration_mock = mocker.patch("ahriman.application.handlers.setup.Setup.create_makepkg_configuration")
    sudo_configuration_mock = mocker.patch("ahriman.application.handlers.setup.Setup.create_sudo_configuration")
    executable_mock = mocker.patch("ahriman.application.handlers.setup.Setup.create_executable")

    Setup.run(args, "x86_64", configuration)
    ahriman_configuration_mock.assert_called_once()
    devtools_configuration_mock.assert_called_once()
    makepkg_configuration_mock.assert_called_once()
    sudo_configuration_mock.assert_called_once()
    executable_mock.assert_called_once()


def test_build_command(args: argparse.Namespace) -> None:
    """
    must generate correct build command name
    """
    args = _default_args(args)
    assert Setup.build_command(args.build_command, "x86_64").name == f"{args.build_command}-x86_64-build"


def test_create_ahriman_configuration(args: argparse.Namespace, configuration: Configuration,
                                      mocker: MockerFixture) -> None:
    """
    must create configuration for the service
    """
    args = _default_args(args)
    mocker.patch("pathlib.Path.open")
    add_section_mock = mocker.patch("configparser.RawConfigParser.add_section")
    set_mock = mocker.patch("configparser.RawConfigParser.set")
    write_mock = mocker.patch("configparser.RawConfigParser.write")

    command = Setup.build_command(args.build_command, "x86_64")
    Setup.create_ahriman_configuration(args, "x86_64", args.repository, configuration.include)
    add_section_mock.assert_has_calls([
        mock.call(Configuration.section_name("build", "x86_64")),
        mock.call("repository"),
        mock.call(Configuration.section_name("sign", "x86_64")),
        mock.call(Configuration.section_name("web", "x86_64")),
    ])
    set_mock.assert_has_calls([
        mock.call(Configuration.section_name("build", "x86_64"), "build_command", str(command)),
        mock.call("repository", "name", args.repository),
        mock.call(Configuration.section_name("sign", "x86_64"), "target",
                  " ".join([target.name.lower() for target in args.sign_target])),
        mock.call(Configuration.section_name("sign", "x86_64"), "key", args.sign_key),
        mock.call(Configuration.section_name("web", "x86_64"), "port", str(args.web_port)),
    ])
    write_mock.assert_called_once()


def test_create_devtools_configuration(args: argparse.Namespace, repository_paths: RepositoryPaths,
                                       mocker: MockerFixture) -> None:
    """
    must create configuration for the devtools
    """
    args = _default_args(args)
    mocker.patch("pathlib.Path.open")
    mocker.patch("configparser.RawConfigParser.set")
    add_section_mock = mocker.patch("configparser.RawConfigParser.add_section")
    write_mock = mocker.patch("configparser.RawConfigParser.write")

    Setup.create_devtools_configuration(args.build_command, "x86_64", args.from_configuration,
                                        args.no_multilib, args.repository, repository_paths)
    add_section_mock.assert_has_calls([
        mock.call("multilib"),
        mock.call(args.repository)
    ])
    write_mock.assert_called_once()


def test_create_devtools_configuration_no_multilib(args: argparse.Namespace, repository_paths: RepositoryPaths,
                                                   mocker: MockerFixture) -> None:
    """
    must create configuration for the devtools without multilib
    """
    args = _default_args(args)
    mocker.patch("pathlib.Path.open")
    mocker.patch("configparser.RawConfigParser.set")
    add_section_mock = mocker.patch("configparser.RawConfigParser.add_section")
    write_mock = mocker.patch("configparser.RawConfigParser.write")

    Setup.create_devtools_configuration(args.build_command, "x86_64", args.from_configuration,
                                        True, args.repository, repository_paths)
    add_section_mock.assert_called_once()
    write_mock.assert_called_once()


def test_create_makepkg_configuration(args: argparse.Namespace, repository_paths: RepositoryPaths,
                                      mocker: MockerFixture) -> None:
    """
    must create makepkg configuration
    """
    args = _default_args(args)
    write_text_mock = mocker.patch("pathlib.Path.write_text")

    Setup.create_makepkg_configuration(args.packager, repository_paths)
    write_text_mock.assert_called_once()


def test_create_sudo_configuration(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must create sudo configuration
    """
    args = _default_args(args)
    chmod_text_mock = mocker.patch("pathlib.Path.chmod")
    write_text_mock = mocker.patch("pathlib.Path.write_text")

    Setup.create_sudo_configuration(args.build_command, "x86_64")
    chmod_text_mock.assert_called_with(0o400)
    write_text_mock.assert_called_once()


def test_create_executable(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must create executable
    """
    args = _default_args(args)
    symlink_text_mock = mocker.patch("pathlib.Path.symlink_to")
    unlink_text_mock = mocker.patch("pathlib.Path.unlink")

    Setup.create_executable(args.build_command, "x86_64")
    symlink_text_mock.assert_called_once()
    unlink_text_mock.assert_called_once()
