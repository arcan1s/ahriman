from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.status import Client
from ahriman.core.support.package_creator import PackageCreator
from ahriman.models.package import Package
from ahriman.models.package_description import PackageDescription
from ahriman.models.package_source import PackageSource
from ahriman.models.remote_source import RemoteSource


def test_package_create(package_creator: PackageCreator, mocker: MockerFixture) -> None:
    """
    must create package
    """
    path = Path("local")
    rmtree_mock = mocker.patch("shutil.rmtree")
    mkdir_mock = mocker.patch("pathlib.Path.mkdir")
    write_mock = mocker.patch("ahriman.core.support.pkgbuild.pkgbuild_generator.PkgbuildGenerator.write_pkgbuild")
    init_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.init")

    package_creator.package_create(path)
    rmtree_mock.assert_called_once_with(path, ignore_errors=True)
    mkdir_mock.assert_called_once_with(mode=0o755, parents=True, exist_ok=True)
    write_mock.assert_called_once_with(path)
    init_mock.assert_called_once_with(path)


def test_package_register(package_creator: PackageCreator, mocker: MockerFixture) -> None:
    """
    must register package
    """
    path = Path("local")
    package = Package(
        base=package_creator.generator.pkgname,
        version=package_creator.generator.pkgver,
        remote=RemoteSource(source=PackageSource.Local),
        packages={package_creator.generator.pkgname: PackageDescription()},
    )
    client_mock = mocker.patch("ahriman.core._Context.get", return_value=Client())
    insert_mock = mocker.patch("ahriman.core.status.Client.set_unknown")
    package_mock = mocker.patch("ahriman.models.package.Package.from_build", return_value=package)

    package_creator.package_register(path)
    package_mock.assert_called_once_with(path, "x86_64", None)
    client_mock.assert_called_once_with(Client)
    insert_mock.assert_called_once_with(package)


def test_run(package_creator: PackageCreator, mocker: MockerFixture) -> None:
    """
    must correctly process package creation
    """
    path = package_creator.configuration.repository_paths.cache_for(package_creator.generator.pkgname)
    create_mock = mocker.patch("ahriman.core.support.package_creator.PackageCreator.package_create")
    register_mock = mocker.patch("ahriman.core.support.package_creator.PackageCreator.package_register")

    package_creator.run()
    create_mock.assert_called_once_with(path)
    register_mock.assert_called_once_with(path)
