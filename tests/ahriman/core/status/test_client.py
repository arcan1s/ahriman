import logging
import pytest

from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.status import Client
from ahriman.core.status.local_client import LocalClient
from ahriman.core.status.web_client import WebClient
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.changes import Changes
from ahriman.models.dependencies import Dependencies
from ahriman.models.event import Event
from ahriman.models.internal_status import InternalStatus
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.package import Package
from ahriman.models.pkgbuild_patch import PkgbuildPatch


def test_load_dummy_client(configuration: Configuration) -> None:
    """
    must load dummy client if no settings and database set
    """
    _, repository_id = configuration.check_loaded()
    assert isinstance(Client.load(repository_id, configuration, report=True), Client)


def test_load_local_client(configuration: Configuration, database: SQLite) -> None:
    """
    must load dummy client if no settings set
    """
    _, repository_id = configuration.check_loaded()
    assert isinstance(Client.load(repository_id, configuration, database, report=True), LocalClient)


def test_load_local_client_disabled(configuration: Configuration, database: SQLite) -> None:
    """
    must load dummy client if report is set to False
    """
    configuration.set_option("web", "host", "localhost")
    configuration.set_option("web", "port", "8080")

    _, repository_id = configuration.check_loaded()
    assert isinstance(Client.load(repository_id, configuration, database, report=False), LocalClient)


def test_load_local_client_disabled_in_configuration(configuration: Configuration, database: SQLite) -> None:
    """
    must load dummy client if disabled in configuration
    """
    configuration.set_option("web", "host", "localhost")
    configuration.set_option("web", "port", "8080")
    configuration.set_option("status", "enabled", "no")

    _, repository_id = configuration.check_loaded()
    assert isinstance(Client.load(repository_id, configuration, database, report=True), LocalClient)


def test_load_web_client_from_address(configuration: Configuration, database: SQLite) -> None:
    """
    must load full client by using address
    """
    configuration.set_option("status", "address", "http://localhost:8080")
    _, repository_id = configuration.check_loaded()
    assert isinstance(Client.load(repository_id, configuration, database, report=True), WebClient)


def test_load_web_client_from_legacy_host(configuration: Configuration, database: SQLite) -> None:
    """
    must load full client if host and port settings set
    """
    configuration.set_option("web", "host", "localhost")
    configuration.set_option("web", "port", "8080")

    _, repository_id = configuration.check_loaded()
    assert isinstance(Client.load(repository_id, configuration, database, report=True), WebClient)


def test_load_web_client_from_legacy_address(configuration: Configuration, database: SQLite) -> None:
    """
    must load full client by using legacy address
    """
    configuration.set_option("web", "address", "http://localhost:8080")
    _, repository_id = configuration.check_loaded()
    assert isinstance(Client.load(repository_id, configuration, database, report=True), WebClient)


def test_load_web_client_from_legacy_unix_socket(configuration: Configuration, database: SQLite) -> None:
    """
    must load full client by using unix socket
    """
    configuration.set_option("web", "unix_socket", "/var/lib/ahriman/ahriman-web.sock")
    _, repository_id = configuration.check_loaded()
    assert isinstance(Client.load(repository_id, configuration, database, report=True), WebClient)


def test_event_add(client: Client) -> None:
    """
    must raise not implemented on event insertion
    """
    with pytest.raises(NotImplementedError):
        client.event_add(Event("", ""))


def test_event_get(client: Client) -> None:
    """
    must raise not implemented on events request
    """
    with pytest.raises(NotImplementedError):
        client.event_get(None, None)


def test_package_changes_get(client: Client, package_ahriman: Package) -> None:
    """
    must raise not implemented on package changes request
    """
    with pytest.raises(NotImplementedError):
        client.package_changes_get(package_ahriman.base)


def test_package_changes_update(client: Client, package_ahriman: Package) -> None:
    """
    must raise not implemented on changes update
    """
    with pytest.raises(NotImplementedError):
        client.package_changes_update(package_ahriman.base, Changes())


def test_package_dependencies_get(client: Client, package_ahriman: Package) -> None:
    """
    must raise not implemented on package dependencies request
    """
    with pytest.raises(NotImplementedError):
        client.package_dependencies_get(package_ahriman.base)


def test_package_dependencies_update(client: Client, package_ahriman: Package) -> None:
    """
    must raise not implemented on dependencies update
    """
    with pytest.raises(NotImplementedError):
        client.package_dependencies_update(package_ahriman.base, Dependencies())


def test_package_get(client: Client, package_ahriman: Package) -> None:
    """
    must raise not implemented on packages get
    """
    with pytest.raises(NotImplementedError):
        assert client.package_get(package_ahriman.base)


def test_package_logs_add(client: Client, package_ahriman: Package, log_record: logging.LogRecord) -> None:
    """
    must process log record addition without exception
    """
    log_record_id = LogRecordId(package_ahriman.base, package_ahriman.version)
    client.package_logs_add(log_record_id, log_record.created, log_record.getMessage())


def test_package_logs_get(client: Client, package_ahriman: Package) -> None:
    """
    must raise not implemented on logs retrieval
    """
    with pytest.raises(NotImplementedError):
        client.package_logs_get(package_ahriman.base)


def test_package_logs_remove(client: Client, package_ahriman: Package) -> None:
    """
    must raise not implemented on logs removal
    """
    with pytest.raises(NotImplementedError):
        client.package_logs_remove(package_ahriman.base, package_ahriman.version)


def test_package_patches_get(client: Client, package_ahriman: Package) -> None:
    """
    must raise not implemented on patches retrieval
    """
    with pytest.raises(NotImplementedError):
        client.package_patches_get(package_ahriman.base, None)


def test_package_patches_remove(client: Client, package_ahriman: Package) -> None:
    """
    must raise not implemented on patches removal
    """
    with pytest.raises(NotImplementedError):
        client.package_patches_remove(package_ahriman.base, None)


def test_package_patches_update(client: Client, package_ahriman: Package) -> None:
    """
    must raise not implemented on patches addition
    """
    with pytest.raises(NotImplementedError):
        client.package_patches_update(package_ahriman.base, PkgbuildPatch(None, ""))


def test_package_remove(client: Client, package_ahriman: Package) -> None:
    """
    must raise not implemented on package removal
    """
    with pytest.raises(NotImplementedError):
        client.package_remove(package_ahriman.base)


def test_package_status_update(client: Client, package_ahriman: Package) -> None:
    """
    must raise not implemented on package update
    """
    with pytest.raises(NotImplementedError):
        client.package_status_update(package_ahriman.base, BuildStatusEnum.Unknown)


def test_package_update(client: Client, package_ahriman: Package) -> None:
    """
    must raise not implemented on package addition
    """
    with pytest.raises(NotImplementedError):
        client.package_update(package_ahriman, BuildStatusEnum.Unknown)


def test_set_building(client: Client, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must set building status to the package
    """
    update_mock = mocker.patch("ahriman.core.status.Client.package_status_update")
    client.set_building(package_ahriman.base)

    update_mock.assert_called_once_with(package_ahriman.base, BuildStatusEnum.Building)


def test_set_failed(client: Client, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must set failed status to the package
    """
    update_mock = mocker.patch("ahriman.core.status.Client.package_status_update")
    client.set_failed(package_ahriman.base)

    update_mock.assert_called_once_with(package_ahriman.base, BuildStatusEnum.Failed)


def test_set_pending(client: Client, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must set building status to the package
    """
    update_mock = mocker.patch("ahriman.core.status.Client.package_status_update")
    client.set_pending(package_ahriman.base)

    update_mock.assert_called_once_with(package_ahriman.base, BuildStatusEnum.Pending)


def test_set_success(client: Client, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must set success status to the package
    """
    update_mock = mocker.patch("ahriman.core.status.Client.package_update")
    client.set_success(package_ahriman)

    update_mock.assert_called_once_with(package_ahriman, BuildStatusEnum.Success)


def test_set_unknown(client: Client, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must add new package with unknown status
    """
    mocker.patch("ahriman.core.status.Client.package_get", return_value=[])
    update_mock = mocker.patch("ahriman.core.status.Client.package_update")
    client.set_unknown(package_ahriman)

    update_mock.assert_called_once_with(package_ahriman, BuildStatusEnum.Unknown)


def test_set_unknown_skip(client: Client, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must skip unknown status update in case if pacakge is already known
    """
    mocker.patch("ahriman.core.status.Client.package_get", return_value=[(package_ahriman, None)])
    update_mock = mocker.patch("ahriman.core.status.Client.package_update")
    client.set_unknown(package_ahriman)

    update_mock.assert_not_called()


def test_status_get(client: Client) -> None:
    """
    must return dummy status for web service
    """
    actual = client.status_get()
    expected = InternalStatus(status=BuildStatus(timestamp=actual.status.timestamp))

    assert actual == expected


def test_status_update(client: Client) -> None:
    """
    must update self status without errors
    """
    client.status_update(BuildStatusEnum.Unknown)
