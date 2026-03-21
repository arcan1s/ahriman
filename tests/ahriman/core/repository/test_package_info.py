import pytest

from dataclasses import replace
from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.core.repository import Repository
from ahriman.models.changes import Changes
from ahriman.models.package import Package


def test_full_depends(repository: Repository, package_ahriman: Package, package_python_schedule: Package,
                      pyalpm_package_ahriman: MagicMock) -> None:
    """
    must extract all dependencies from the package
    """
    package_python_schedule.packages[package_python_schedule.base].provides = ["python3-schedule"]

    database_mock = MagicMock()
    database_mock.pkgcache = [pyalpm_package_ahriman]
    repository.pacman = MagicMock()
    repository.pacman.handle.get_syncdbs.return_value = [database_mock]

    assert repository.full_depends(package_ahriman, [package_python_schedule]) == package_ahriman.depends

    package_python_schedule.packages[package_python_schedule.base].depends = [package_ahriman.base]
    expected = sorted(set(package_python_schedule.depends + package_ahriman.depends))
    assert repository.full_depends(package_python_schedule, [package_python_schedule]) == expected


def test_load_archives(repository: Repository, package_ahriman: Package, package_python_schedule: Package,
                       mocker: MockerFixture) -> None:
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
    mocker.patch("ahriman.core.status.local_client.LocalClient.package_get", return_value=[
        (package_ahriman, None),
    ])

    packages = repository.load_archives([Path("a.pkg.tar.xz"), Path("b.pkg.tar.xz"), Path("c.pkg.tar.xz")])
    assert len(packages) == 2
    assert {package.base for package in packages} == {package_ahriman.base, package_python_schedule.base}

    archives = sum((list(package.packages.keys()) for package in packages), start=[])
    assert len(archives) == 3
    expected = set(package_ahriman.packages.keys())
    expected.update(package_python_schedule.packages.keys())
    assert set(archives) == expected


def test_load_archives_failed(repository: Repository, mocker: MockerFixture) -> None:
    """
    must skip packages which cannot be loaded
    """
    mocker.patch("ahriman.models.package.Package.from_archive", side_effect=Exception)
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


def test_load_archives_all_versions(repository: Repository, package_ahriman: Package,
                                    mocker: MockerFixture) -> None:
    """
    must load packages with different versions keeping all when latest_only is False
    """
    mocker.patch("ahriman.models.package.Package.from_archive",
                 side_effect=[package_ahriman, replace(package_ahriman, version="0.0.1-1")])
    mocker.patch("ahriman.core.status.local_client.LocalClient.package_get", return_value=[])

    packages = repository.load_archives([Path("a.pkg.tar.xz"), Path("b.pkg.tar.xz")], latest_only=False)
    assert len(packages) == 2


def test_package_archives(repository: Repository, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must load package archives sorted by version
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("pathlib.Path.iterdir")
    load_mock = mocker.patch("ahriman.core.repository.package_info.PackageInfo.load_archives",
                             return_value=[replace(package_ahriman, version=str(i)) for i in range(5)])

    result = repository.package_archives(package_ahriman.base)
    assert len(result) == 5
    assert [p.version for p in result] == [str(i) for i in range(5)]
    load_mock.assert_called_once_with(pytest.helpers.anyvar(int), latest_only=False)


def test_package_archives_no_directory(repository: Repository, package_ahriman: Package,
                                       mocker: MockerFixture) -> None:
    """
    must return empty list if archive directory does not exist
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    assert repository.package_archives(package_ahriman.base) == []


def test_package_archives_architecture_mismatch(repository: Repository, package_ahriman: Package,
                                                mocker: MockerFixture) -> None:
    """
    must skip packages with mismatched architecture
    """
    package_ahriman.packages[package_ahriman.base].architecture = "i686"

    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("pathlib.Path.iterdir")
    mocker.patch("ahriman.core.repository.package_info.PackageInfo.load_archives",
                 return_value=[package_ahriman])

    result = repository.package_archives(package_ahriman.base)
    assert len(result) == 0


def test_package_archives_lookup(repository: Repository, package_ahriman: Package, package_python_schedule: Package,
                                 mocker: MockerFixture) -> None:
    """
    must existing packages which match the version
    """
    archives_mock = mocker.patch("ahriman.core.repository.package_info.PackageInfo.package_archives", return_value=[
        package_ahriman,
        package_python_schedule,
        replace(package_ahriman, version="1"),
    ])
    glob_mock = mocker.patch("pathlib.Path.glob", return_value=[Path("1.pkg.tar.xz")])

    assert repository.package_archives_lookup(package_ahriman) == [Path("1.pkg.tar.xz")]
    archives_mock.assert_called_once_with(package_ahriman.base)
    glob_mock.assert_called_once_with(f"{package_ahriman.packages[package_ahriman.base].filename}*")


def test_package_archives_lookup_version_mismatch(repository: Repository, package_ahriman: Package,
                                                  mocker: MockerFixture) -> None:
    """
    must return nothing if no packages found with the same version
    """
    mocker.patch("ahriman.core.repository.package_info.PackageInfo.package_archives",
                 return_value=[replace(package_ahriman, version="1")])
    assert repository.package_archives_lookup(package_ahriman) == []


def test_package_archives_lookup_architecture_mismatch(repository: Repository, package_ahriman: Package,
                                                       mocker: MockerFixture) -> None:
    """
    must return nothing if architecture doesn't match
    """
    mocker.patch("ahriman.core.repository.package_info.PackageInfo.package_archives", return_value=[])
    assert repository.package_archives_lookup(package_ahriman) == []


def test_package_archives_lookup_no_archive_directory(repository: Repository, package_ahriman: Package,
                                                      mocker: MockerFixture) -> None:
    """
    must return nothing if no archive directory found
    """
    mocker.patch("ahriman.core.repository.package_info.PackageInfo.package_archives", return_value=[])
    assert repository.package_archives_lookup(package_ahriman) == []


def test_package_changes(repository: Repository, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must load package changes
    """
    changes = Changes("sha", "change")
    load_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.load", return_value="sha2")
    changes_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.changes", return_value=changes)

    assert repository.package_changes(package_ahriman, changes.last_commit_sha) == changes
    load_mock.assert_called_once_with(
        pytest.helpers.anyvar(int), package_ahriman, [], repository.configuration.repository_paths)
    changes_mock.assert_called_once_with(pytest.helpers.anyvar(int), changes.last_commit_sha)


def test_package_changes_skip(repository: Repository, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must skip loading package changes if no new commits
    """
    mocker.patch("ahriman.core.build_tools.sources.Sources.load", return_value="sha")
    changes_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.changes")

    assert repository.package_changes(package_ahriman, "sha") is None
    changes_mock.assert_not_called()


def test_packages(repository: Repository, package_ahriman: Package, package_python_schedule: Package,
                  mocker: MockerFixture) -> None:
    """
    must return repository packages
    """
    mocker.patch("pathlib.Path.iterdir")
    load_mock = mocker.patch("ahriman.core.repository.package_info.PackageInfo.load_archives",
                             return_value=[package_ahriman, package_python_schedule])
    assert repository.packages() == [package_ahriman, package_python_schedule]
    # it uses filter object, so we cannot verify argument list =/
    load_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_packages_filter(repository: Repository, package_ahriman: Package, package_python_schedule: Package,
                         mocker: MockerFixture) -> None:
    """
    must filter result by bases
    """
    mocker.patch("pathlib.Path.iterdir")
    mocker.patch("ahriman.core.repository.package_info.PackageInfo.load_archives",
                 return_value=[package_ahriman, package_python_schedule])
    assert repository.packages([package_ahriman.base]) == [package_ahriman]


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
    assert repository.packages_depend_on([package_ahriman], {"python-srcinfo"}) == [package_ahriman]


def test_packages_depend_on_empty(repository: Repository, package_ahriman: Package, package_python_schedule: Package,
                                  mocker: MockerFixture) -> None:
    """
    must return all packages in case if no filter is provided
    """
    mocker.patch("ahriman.core.repository.repository.Repository.packages",
                 return_value=[package_ahriman, package_python_schedule])
    assert repository.packages_depend_on([package_ahriman, package_python_schedule], None) == \
        [package_ahriman, package_python_schedule]
