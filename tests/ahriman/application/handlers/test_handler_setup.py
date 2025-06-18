import argparse
import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from typing import Any
from unittest.mock import call as MockCall
from urllib.parse import quote_plus as url_encode

from ahriman.application.handlers.setup import Setup
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.exceptions import MissingArchitectureError
from ahriman.core.repository import Repository
from ahriman.models.repository_id import RepositoryId
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
    args.architecture = "x86_64"
    args.build_as_user = "ahriman"
    args.from_configuration = Path("/usr/share/devtools/pacman.conf.d/extra.conf")
    args.generate_salt = True
    args.makeflags_jobs = True
    args.mirror = "mirror"
    args.multilib = True
    args.packager = "ahriman bot <ahriman@example.com>"
    args.repository = "aur"
    args.server = None
    args.sign_key = "key"
    args.sign_target = [SignSettings.Packages]
    args.web_port = 8080
    args.web_unix_socket = Path("/var/lib/ahriman/ahriman-web.sock")
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
             database: SQLite, repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    ahriman_configuration_mock = mocker.patch("ahriman.application.handlers.setup.Setup.configuration_create_ahriman")
    devtools_configuration_mock = mocker.patch("ahriman.application.handlers.setup.Setup.configuration_create_devtools")
    makepkg_configuration_mock = mocker.patch("ahriman.application.handlers.setup.Setup.configuration_create_makepkg")
    sudo_configuration_mock = mocker.patch("ahriman.application.handlers.setup.Setup.configuration_create_sudo")
    executable_mock = mocker.patch("ahriman.application.handlers.setup.Setup.executable_create")
    init_mock = mocker.patch("ahriman.core.alpm.repo.Repo.init")

    _, repository_id = configuration.check_loaded()
    Setup.run(args, repository_id, configuration, report=False)
    ahriman_configuration_mock.assert_called_once_with(args, repository_id, configuration)
    devtools_configuration_mock.assert_called_once_with(
        repository_id, args.from_configuration, args.mirror, args.multilib, f"file://{repository_paths.repository}")
    makepkg_configuration_mock.assert_called_once_with(args.packager, args.makeflags_jobs, repository_paths)
    sudo_configuration_mock.assert_called_once_with(repository_paths, repository_id)
    executable_mock.assert_called_once_with(repository_paths, repository_id)
    init_mock.assert_called_once_with()


def test_run_no_architecture_or_repository(configuration: Configuration) -> None:
    """
    must raise MissingArchitectureError if either architecture or repository are not supplied
    """
    _, repository_id = configuration.check_loaded()

    args = argparse.Namespace(architecture=None, command="service-setup", repository=None)
    with pytest.raises(MissingArchitectureError):
        Setup.run(args, repository_id, configuration, report=False)

    args = argparse.Namespace(architecture=[repository_id.architecture], command="service-setup", repository=None)
    with pytest.raises(MissingArchitectureError):
        Setup.run(args, repository_id, configuration, report=False)

    args = argparse.Namespace(architecture=None, command="service-setup", repository=[repository_id.name])
    with pytest.raises(MissingArchitectureError):
        Setup.run(args, repository_id, configuration, report=False)


def test_run_with_server(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                         database: SQLite, mocker: MockerFixture) -> None:
    """
    must run command with server specified
    """
    args = _default_args(args)
    args.server = "server"
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.application.handlers.setup.Setup.configuration_create_ahriman")
    mocker.patch("ahriman.application.handlers.setup.Setup.configuration_create_makepkg")
    mocker.patch("ahriman.application.handlers.setup.Setup.configuration_create_sudo")
    mocker.patch("ahriman.application.handlers.setup.Setup.executable_create")
    mocker.patch("ahriman.core.alpm.repo.Repo.init")
    devtools_configuration_mock = mocker.patch("ahriman.application.handlers.setup.Setup.configuration_create_devtools")

    _, repository_id = configuration.check_loaded()
    Setup.run(args, repository_id, configuration, report=False)
    devtools_configuration_mock.assert_called_once_with(
        repository_id, args.from_configuration, args.mirror, args.multilib, "server")


def test_build_command(repository_id: RepositoryId) -> None:
    """
    must generate correct build command name
    """
    path = Path("local")

    build_command = Setup.build_command(path, repository_id)
    assert build_command.name == f"{repository_id.name}-{repository_id.architecture}-build"
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
    remove_mock = mocker.patch("pathlib.Path.unlink", autospec=True)
    _, repository_id = configuration.check_loaded()
    command = Setup.build_command(repository_paths.root, repository_id)

    Setup.configuration_create_ahriman(args, repository_id, configuration)
    set_option_mock.assert_has_calls([
        MockCall(Configuration.section_name("build", repository_id.name, repository_id.architecture), "build_command",
                 str(command)),
        MockCall("repository", "name", repository_id.name),
        MockCall(Configuration.section_name("build", repository_id.name, repository_id.architecture),
                 "makechrootpkg_flags", f"-U {args.build_as_user}"),
        MockCall(Configuration.section_name(
            "alpm", repository_id.name, repository_id.architecture), "mirror", args.mirror),
        MockCall(Configuration.section_name("sign", repository_id.name, repository_id.architecture), "target",
                 " ".join([target.name.lower() for target in args.sign_target])),
        MockCall(Configuration.section_name("sign", repository_id.name, repository_id.architecture), "key",
                 args.sign_key),
        MockCall("web", "port", str(args.web_port)),
        MockCall("status", "address", f"http://127.0.0.1:{str(args.web_port)}"),
        MockCall("web", "unix_socket", str(args.web_unix_socket)),
        MockCall("status", "address", f"http+unix://{url_encode(str(args.web_unix_socket))}"),
        MockCall("auth", "salt", pytest.helpers.anyvar(str, strict=True)),
    ])
    write_mock.assert_called_once_with(pytest.helpers.anyvar(int))
    remove_mock.assert_called_once_with(configuration.include / "00-setup-overrides.ini", missing_ok=True)


def test_configuration_create_ahriman_no_multilib(args: argparse.Namespace, configuration: Configuration,
                                                  mocker: MockerFixture) -> None:
    """
    must create configuration for the service without multilib repository
    """
    args = _default_args(args)
    args.multilib = False
    mocker.patch("pathlib.Path.open")
    mocker.patch("ahriman.core.configuration.Configuration.write")
    set_option_mock = mocker.patch("ahriman.core.configuration.Configuration.set_option")

    _, repository_id = configuration.check_loaded()
    Setup.configuration_create_ahriman(args, repository_id, configuration)
    set_option_mock.assert_has_calls([
        MockCall(Configuration.section_name("alpm", repository_id.name, repository_id.architecture), "mirror",
                 args.mirror),
    ])  # non-strict check called intentionally


def test_configuration_create_devtools(args: argparse.Namespace, configuration: Configuration,
                                       mocker: MockerFixture) -> None:
    """
    must create configuration for the devtools
    """
    args = _default_args(args)
    mocker.patch("pathlib.Path.open")
    mocker.patch("ahriman.core.configuration.Configuration.set")
    add_section_mock = mocker.patch("ahriman.core.configuration.Configuration.add_section")
    write_mock = mocker.patch("ahriman.core.configuration.Configuration.write")

    _, repository_id = configuration.check_loaded()
    Setup.configuration_create_devtools(repository_id, args.from_configuration, None, args.multilib, "server")
    add_section_mock.assert_has_calls([MockCall("multilib"), MockCall(repository_id.name)])
    write_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_configuration_create_devtools_mirror(args: argparse.Namespace, configuration: Configuration,
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

    _, repository_id = configuration.check_loaded()
    Setup.configuration_create_devtools(repository_id, args.from_configuration, args.mirror, args.multilib, "server")
    get_mock.assert_has_calls([MockCall("core", "Include", fallback=None), MockCall("extra", "Include", fallback=None)])
    remove_option_mock.assert_called_once_with("core", "Include")
    set_option_mock.assert_has_calls([MockCall("core", "Server", args.mirror)])  # non-strict check called intentionally


def test_configuration_create_devtools_no_multilib(args: argparse.Namespace, configuration: Configuration,
                                                   mocker: MockerFixture) -> None:
    """
    must create configuration for the devtools without multilib
    """
    args = _default_args(args)
    mocker.patch("pathlib.Path.open")
    mocker.patch("ahriman.core.configuration.Configuration.set")
    write_mock = mocker.patch("ahriman.core.configuration.Configuration.write")

    _, repository_id = configuration.check_loaded()
    Setup.configuration_create_devtools(repository_id, args.from_configuration, args.mirror, False, "server")
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


def test_configuration_create_sudo(configuration: Configuration, repository_paths: RepositoryPaths,
                                   mocker: MockerFixture) -> None:
    """
    must create sudo configuration
    """
    chmod_text_mock = mocker.patch("pathlib.Path.chmod")
    write_text_mock = mocker.patch("pathlib.Path.write_text")

    _, repository_id = configuration.check_loaded()
    Setup.configuration_create_sudo(repository_paths, repository_id)
    chmod_text_mock.assert_called_once_with(0o400)
    write_text_mock.assert_called_once_with(pytest.helpers.anyvar(str, True), encoding="utf8")


def test_executable_create(configuration: Configuration, repository_paths: RepositoryPaths,
                           mocker: MockerFixture) -> None:
    """
    must create executable
    """
    chown_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.chown")
    symlink_mock = mocker.patch("pathlib.Path.symlink_to")
    unlink_mock = mocker.patch("pathlib.Path.unlink")

    _, repository_id = configuration.check_loaded()
    Setup.executable_create(repository_paths, repository_id)
    chown_mock.assert_called_once_with(Setup.build_command(repository_paths.root, repository_id))
    symlink_mock.assert_called_once_with(Setup.ARCHBUILD_COMMAND_PATH)
    unlink_mock.assert_called_once_with(missing_ok=True)


def test_disallow_multi_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Setup.ALLOW_MULTI_ARCHITECTURE_RUN
