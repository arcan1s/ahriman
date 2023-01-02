import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.repository import Repository
from ahriman.core.sign.gpg import GPG
from ahriman.models.context_key import ContextKey
from ahriman.models.package import Package


def test_load(configuration: Configuration, database: SQLite, mocker: MockerFixture) -> None:
    """
    must correctly load instance
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    context_mock = mocker.patch("ahriman.core.repository.Repository._set_context")
    Repository.load("x86_64", configuration, database, report=False, unsafe=False)
    context_mock.assert_called_once_with()


def test_set_context(configuration: Configuration, database: SQLite, mocker: MockerFixture) -> None:
    """
    must set context variables
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    set_mock = mocker.patch("ahriman.core._Context.set")

    instance = Repository.load("x86_64", configuration, database, report=False, unsafe=False)
    set_mock.assert_has_calls([
        MockCall(ContextKey("database", SQLite), instance.database, strict=False),
        MockCall(ContextKey("configuration", Configuration), instance.configuration, strict=False),
        MockCall(ContextKey("pacman", Pacman), instance.pacman, strict=False),
        MockCall(ContextKey("sign", GPG), instance.sign, strict=False),
        MockCall(ContextKey("repository", Repository), instance, strict=False),
    ])


def test_load_archives(package_ahriman: Package, package_python_schedule: Package,
                       repository: Repository, mocker: MockerFixture) -> None:
    """
    must return all packages grouped by package base
    """
    single_packages = [
        Package(base=package_python_schedule.base,
                version=package_python_schedule.version,
                remote=package_python_schedule.remote,
                packages={package: props})
        for package, props in package_python_schedule.packages.items()
    ] + [package_ahriman]
    mocker.patch("ahriman.models.package.Package.from_archive", side_effect=single_packages)

    packages = repository.load_archives([Path("a.pkg.tar.xz"), Path("b.pkg.tar.xz"), Path("c.pkg.tar.xz")])
    assert len(packages) == 2
    assert {package.base for package in packages} == {package_ahriman.base, package_python_schedule.base}

    archives = sum([list(package.packages.keys()) for package in packages], start=[])
    assert len(archives) == 3
    expected = set(package_ahriman.packages.keys())
    expected.update(package_python_schedule.packages.keys())
    assert set(archives) == expected


def test_load_archives_failed(repository: Repository, mocker: MockerFixture) -> None:
    """
    must skip packages which cannot be loaded
    """
    mocker.patch("ahriman.models.package.Package.from_archive", side_effect=Exception())
    assert not repository.load_archives([Path("a.pkg.tar.xz")])


def test_load_archives_not_package(repository: Repository) -> None:
    """
    must skip not packages from iteration
    """
    assert not repository.load_archives([Path("a.tar.xz")])


def test_load_archives_different_version(repository: Repository, package_python_schedule: Package,
                                         mocker: MockerFixture) -> None:
    """
    must load packages with different versions choosing maximal
    """
    single_packages = [
        Package(base=package_python_schedule.base,
                version=package_python_schedule.version,
                remote=package_python_schedule.remote,
                packages={package: props})
        for package, props in package_python_schedule.packages.items()
    ]
    single_packages[0].version = "0.0.1-1"
    mocker.patch("ahriman.models.package.Package.from_archive", side_effect=single_packages)

    packages = repository.load_archives([Path("a.pkg.tar.xz"), Path("b.pkg.tar.xz")])
    assert len(packages) == 1
    assert packages[0].version == package_python_schedule.version


def test_packages(repository: Repository, mocker: MockerFixture) -> None:
    """
    must return repository packages
    """
    load_mock = mocker.patch("ahriman.core.repository.repository.Repository.load_archives")
    repository.packages()
    # it uses filter object, so we cannot verify argument list =/
    load_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_packages_built(repository: Repository, mocker: MockerFixture) -> None:
    """
    must return build packages
    """
    mocker.patch("pathlib.Path.iterdir", return_value=[Path("a.tar.xz"), Path("b.pkg.tar.xz")])
    assert repository.packages_built() == [Path("b.pkg.tar.xz")]


def test_packages_depend_on(repository: Repository, package_ahriman: Package, package_python_schedule: Package,
                            mocker: MockerFixture) -> None:
    """
    must filter packages by depends list
    """
    mocker.patch("ahriman.core.repository.repository.Repository.packages",
                 return_value=[package_ahriman, package_python_schedule])
    assert repository.packages_depend_on([package_ahriman], ["python-aur"]) == [package_ahriman]


def test_packages_depend_on_empty(repository: Repository, package_ahriman: Package, package_python_schedule: Package,
                                  mocker: MockerFixture) -> None:
    """
    must return all packages in case if no filter is provided
    """
    mocker.patch("ahriman.core.repository.repository.Repository.packages",
                 return_value=[package_ahriman, package_python_schedule])
    assert repository.packages_depend_on([package_ahriman, package_python_schedule], None) ==\
        [package_ahriman, package_python_schedule]
