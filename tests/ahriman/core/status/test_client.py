from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.status.client import Client
from ahriman.core.status.web_client import WebClient
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.internal_status import InternalStatus
from ahriman.models.package import Package


def test_load_dummy_client(configuration: Configuration) -> None:
    """
    must load dummy client if no settings set
    """
    assert isinstance(Client.load(configuration), Client)


def test_load_full_client(configuration: Configuration) -> None:
    """
    must load full client if settings set
    """
    configuration.set_option("web", "host", "localhost")
    configuration.set_option("web", "port", "8080")
    assert isinstance(Client.load(configuration), WebClient)


def test_load_full_client_from_address(configuration: Configuration) -> None:
    """
    must load full client by using address
    """
    configuration.set_option("web", "address", "http://localhost:8080")
    assert isinstance(Client.load(configuration), WebClient)


def test_add(client: Client, package_ahriman: Package) -> None:
    """
    must process package addition without errors
    """
    client.add(package_ahriman, BuildStatusEnum.Unknown)


def test_get(client: Client, package_ahriman: Package) -> None:
    """
    must return empty package list
    """
    assert client.get(package_ahriman.base) == []
    assert client.get(None) == []


def test_get_internal(client: Client) -> None:
    """
    must return dummy status for web service
    """
    actual = client.get_internal()
    expected = InternalStatus(status=BuildStatus(timestamp=actual.status.timestamp))

    assert actual == expected


def test_remove(client: Client, package_ahriman: Package) -> None:
    """
    must process remove without errors
    """
    client.remove(package_ahriman.base)


def test_update(client: Client, package_ahriman: Package) -> None:
    """
    must update package status without errors
    """
    client.update(package_ahriman.base, BuildStatusEnum.Unknown)


def test_update_self(client: Client) -> None:
    """
    must update self status without errors
    """
    client.update_self(BuildStatusEnum.Unknown)


def test_set_building(client: Client, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must set building status to the package
    """
    update_mock = mocker.patch("ahriman.core.status.client.Client.update")
    client.set_building(package_ahriman.base)

    update_mock.assert_called_once_with(package_ahriman.base, BuildStatusEnum.Building)


def test_set_failed(client: Client, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must set failed status to the package
    """
    update_mock = mocker.patch("ahriman.core.status.client.Client.update")
    client.set_failed(package_ahriman.base)

    update_mock.assert_called_once_with(package_ahriman.base, BuildStatusEnum.Failed)


def test_set_pending(client: Client, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must set building status to the package
    """
    update_mock = mocker.patch("ahriman.core.status.client.Client.update")
    client.set_pending(package_ahriman.base)

    update_mock.assert_called_once_with(package_ahriman.base, BuildStatusEnum.Pending)


def test_set_success(client: Client, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must set success status to the package
    """
    add_mock = mocker.patch("ahriman.core.status.client.Client.add")
    client.set_success(package_ahriman)

    add_mock.assert_called_once_with(package_ahriman, BuildStatusEnum.Success)


def test_set_unknown(client: Client, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must add new package with unknown status
    """
    add_mock = mocker.patch("ahriman.core.status.client.Client.add")
    client.set_unknown(package_ahriman)

    add_mock.assert_called_once_with(package_ahriman, BuildStatusEnum.Unknown)
