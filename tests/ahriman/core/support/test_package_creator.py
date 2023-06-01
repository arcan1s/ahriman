import pytest

from pytest_mock import MockerFixture

from ahriman.core.database import SQLite
from ahriman.core.support.package_creator import PackageCreator
from ahriman.models.context_key import ContextKey
from ahriman.models.package import Package
from ahriman.models.package_description import PackageDescription


def test_run(package_creator: PackageCreator, database: SQLite, mocker: MockerFixture) -> None:
    """
    must correctly process package creation
    """
    package = Package(
        base=package_creator.generator.pkgname,
        version=package_creator.generator.pkgver,
        remote=None,
        packages={package_creator.generator.pkgname: PackageDescription()},
    )
    local_path = package_creator.configuration.repository_paths.cache_for(package_creator.generator.pkgname)

    rmtree_mock = mocker.patch("shutil.rmtree")
    database_mock = mocker.patch("ahriman.core._Context.get", return_value=database)
    init_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.init")
    insert_mock = mocker.patch("ahriman.core.database.SQLite.package_update")
    mkdir_mock = mocker.patch("pathlib.Path.mkdir")
    package_mock = mocker.patch("ahriman.models.package.Package.from_build", return_value=package)
    write_mock = mocker.patch("ahriman.core.support.pkgbuild.pkgbuild_generator.PkgbuildGenerator.write_pkgbuild")

    package_creator.run()
    rmtree_mock.assert_called_once_with(local_path, ignore_errors=True)
    mkdir_mock.assert_called_once_with(mode=0o755, parents=True, exist_ok=True)
    write_mock.assert_called_once_with(local_path)
    init_mock.assert_called_once_with(local_path)

    package_mock.assert_called_once_with(local_path, "x86_64", None)
    database_mock.assert_called_once_with(ContextKey("database", SQLite))
    insert_mock.assert_called_once_with(package, pytest.helpers.anyvar(int))
