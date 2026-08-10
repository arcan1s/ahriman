import argparse
import multiprocessing
import os
import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from typing import Any
from unittest.mock import call as MockCall
from urllib.parse import quote_plus as url_encode

from ahriman.application.handlers.setup import Setup
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.exceptions import InitializeError, MissingArchitectureError
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
    local = Path("local")
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mkdir_mock = mocker.patch("ahriman.application.handlers.setup.Setup.configuration_create_directory",
                              return_value=local)
    ahriman_configuration_mock = mocker.patch("ahriman.application.handlers.setup.Setup.configuration_create_ahriman")
    devtools_configuration_mock = mocker.patch("ahriman.application.handlers.setup.Setup.configuration_create_devtools")
    init_mock = mocker.patch("ahriman.core.alpm.repo.Repo.init")
    owner_guard_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.preserve_owner")

    _, repository_id = configuration.check_loaded()
    Setup.run(args, repository_id, configuration, report=False)
    owner_guard_mock.assert_called_once_with()
    mkdir_mock.assert_called_once_with(configuration)
    ahriman_configuration_mock.assert_called_once_with(args, repository_id, configuration, local)
    devtools_configuration_mock.assert_called_once_with(
        repository_id,
        args.from_configuration,
        configuration.getpath("build", "devtools_configs"),
        args.mirror,
        args.multilib,
        f"file://{repository_paths.repository}",
    )
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
    mocker.patch("ahriman.core.alpm.repo.Repo.init")
    devtools_configuration_mock = mocker.patch("ahriman.application.handlers.setup.Setup.configuration_create_devtools")

    _, repository_id = configuration.check_loaded()
    Setup.run(args, repository_id, configuration, report=False)
    devtools_configuration_mock.assert_called_once_with(
        repository_id,
        args.from_configuration,
        configuration.getpath("build", "devtools_configs"),
        args.mirror,
        args.multilib,
        "server",
    )


def test_configuration_create_ahriman(args: argparse.Namespace, configuration: Configuration, tmp_path: Path,
                                      mocker: MockerFixture) -> None:
    """
    must create configuration for the service
    """
    args = _default_args(args)
    mocker.patch("pathlib.Path.open")
    set_option_mock = mocker.patch("ahriman.core.configuration.Configuration.set_option")
    write_mock = mocker.patch("ahriman.core.configuration.Configuration.write")
    _, repository_id = configuration.check_loaded()

    Setup.configuration_create_ahriman(args, repository_id, configuration, tmp_path)
    set_option_mock.assert_has_calls([
        MockCall("repository", "name", repository_id.name),
        MockCall(Configuration.section_name("build", repository_id.name, repository_id.architecture),
                 "packager", args.packager),
        MockCall(Configuration.section_name("build", repository_id.name, repository_id.architecture),
                 "make_flags", f"-j{multiprocessing.cpu_count()}"),
        MockCall(Configuration.section_name("build", repository_id.name, repository_id.architecture),
                 "makechrootpkg_flags", f"-U {args.build_as_user}"),
        MockCall(Configuration.section_name("alpm", repository_id.name, repository_id.architecture),
                 "mirror", args.mirror),
        MockCall(Configuration.section_name("sign", repository_id.name, repository_id.architecture),
                 "target", " ".join([target.name.lower() for target in args.sign_target])),
        MockCall(Configuration.section_name("sign", repository_id.name, repository_id.architecture),
                 "key", args.sign_key),
        MockCall("web", "port", str(args.web_port)),
        MockCall("status", "address", f"http://127.0.0.1:{str(args.web_port)}"),
        MockCall("web", "unix_socket", str(args.web_unix_socket)),
        MockCall("status", "address", f"http+unix://{url_encode(str(args.web_unix_socket))}"),
        MockCall("auth", "salt", pytest.helpers.anyvar(str, strict=True)),
    ])
    write_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_configuration_create_ahriman_no_multilib(args: argparse.Namespace, configuration: Configuration,
                                                  tmp_path: Path, mocker: MockerFixture) -> None:
    """
    must create configuration for the service without multilib repository
    """
    args = _default_args(args)
    args.multilib = False
    mocker.patch("pathlib.Path.open")
    mocker.patch("ahriman.core.configuration.Configuration.write")
    set_option_mock = mocker.patch("ahriman.core.configuration.Configuration.set_option")

    _, repository_id = configuration.check_loaded()
    Setup.configuration_create_ahriman(args, repository_id, configuration, tmp_path)
    set_option_mock.assert_has_calls([
        MockCall(Configuration.section_name("alpm", repository_id.name, repository_id.architecture), "mirror",
                 args.mirror),
    ])  # non-strict check called intentionally


def test_configuration_create_devtools(args: argparse.Namespace, configuration: Configuration, tmp_path: Path,
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
    Setup.configuration_create_devtools(repository_id, args.from_configuration, tmp_path, None, args.multilib, "server")
    add_section_mock.assert_has_calls([MockCall("multilib"), MockCall(repository_id.name)])
    write_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_configuration_create_devtools_mirror(args: argparse.Namespace, configuration: Configuration, tmp_path: Path,
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
    Setup.configuration_create_devtools(
        repository_id,
        args.from_configuration,
        tmp_path,
        args.mirror,
        args.multilib,
        "server",
    )
    get_mock.assert_has_calls([MockCall("core", "Include", fallback=None), MockCall("extra", "Include", fallback=None)])
    remove_option_mock.assert_called_once_with("core", "Include")
    set_option_mock.assert_has_calls([MockCall("core", "Server", args.mirror)])  # non-strict check called intentionally


def test_configuration_create_devtools_no_multilib(args: argparse.Namespace, configuration: Configuration,
                                                   tmp_path: Path, mocker: MockerFixture) -> None:
    """
    must create configuration for the devtools without multilib
    """
    args = _default_args(args)
    mocker.patch("pathlib.Path.open")
    mocker.patch("ahriman.core.configuration.Configuration.set")
    write_mock = mocker.patch("ahriman.core.configuration.Configuration.write")

    _, repository_id = configuration.check_loaded()
    Setup.configuration_create_devtools(repository_id, args.from_configuration, tmp_path, args.mirror, False, "server")
    write_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_configuration_create_directory(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must create writable directory for includes
    """
    configuration.set_option("settings", "include", f"/path1 /path2 /path3")
    mkdir_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.ensure_exists",
                              side_effect=[OSError, "/path2", "/path3"])
    access_mock = mocker.patch("os.access", side_effect=[False, True])

    assert Setup.configuration_create_directory(configuration) == "/path3"
    mkdir_mock.assert_has_calls([MockCall(Path("/path1")), MockCall(Path("/path2")), MockCall(Path("/path3"))])
    access_mock.assert_has_calls([MockCall("/path2", os.W_OK | os.X_OK), MockCall("/path3", os.W_OK | os.X_OK)])


def test_configuration_create_directory_no_writable(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must raise InitializeError if no writable directories found
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.ensure_exists", side_effect=OSError)
    with pytest.raises(InitializeError):
        Setup.configuration_create_directory(configuration)


def test_disallow_multi_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Setup.ALLOW_MULTI_ARCHITECTURE_RUN
