import pytest

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.repository.package_info import PackageInfo
from ahriman.models.changes import Changes
from ahriman.models.package import Package


def test_load_archives(package_ahriman: Package, package_python_schedule: Package,
                       package_info: PackageInfo, mocker: MockerFixture) -> None:
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
    mocker.patch("ahriman.core.database.SQLite.remotes_get", return_value={
        package_ahriman.base: package_ahriman.base
    })

    packages = package_info.load_archives([Path("a.pkg.tar.xz"), Path("b.pkg.tar.xz"), Path("c.pkg.tar.xz")])
    assert len(packages) == 2
    assert {package.base for package in packages} == {package_ahriman.base, package_python_schedule.base}

    archives = sum([list(package.packages.keys()) for package in packages], start=[])
    assert len(archives) == 3
    expected = set(package_ahriman.packages.keys())
    expected.update(package_python_schedule.packages.keys())
    assert set(archives) == expected


def test_load_archives_failed(package_info: PackageInfo, mocker: MockerFixture) -> None:
    """
    must skip packages which cannot be loaded
    """
    mocker.patch("ahriman.models.package.Package.from_archive", side_effect=Exception())
    assert not package_info.load_archives([Path("a.pkg.tar.xz")])


def test_load_archives_not_package(package_info: PackageInfo) -> None:
    """
    must skip not packages from iteration
    """
    assert not package_info.load_archives([Path("a.tar.xz")])


def test_load_archives_different_version(package_info: PackageInfo, package_python_schedule: Package,
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

    packages = package_info.load_archives([Path("a.pkg.tar.xz"), Path("b.pkg.tar.xz")])
    assert len(packages) == 1
    assert packages[0].version == package_python_schedule.version


def test_package_changes(package_info: PackageInfo, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must load package changes
    """
    changes = Changes("sha", "change")
    load_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.load", return_value="sha2")
    changes_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.changes", return_value=changes.changes)

    assert package_info.package_changes(package_ahriman, changes.last_commit_sha) == changes
    load_mock.assert_called_once_with(pytest.helpers.anyvar(int), package_ahriman, [], package_info.paths)
    changes_mock.assert_called_once_with(pytest.helpers.anyvar(int), changes.last_commit_sha)


def test_package_changes_skip(package_info: PackageInfo, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must skip loading package changes if no new commits
    """
    changes = Changes("sha")
    mocker.patch("ahriman.core.build_tools.sources.Sources.load", return_value=changes.last_commit_sha)
    changes_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.changes")

    assert package_info.package_changes(package_ahriman, changes.last_commit_sha) == changes
    changes_mock.assert_not_called()


def test_packages(package_info: PackageInfo, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return repository packages
    """
    mocker.patch("pathlib.Path.iterdir", return_value=[package_ahriman])
    load_mock = mocker.patch("ahriman.core.repository.package_info.PackageInfo.load_archives")
    package_info.packages()
    # it uses filter object, so we cannot verify argument list =/
    load_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_packages_built(package_info: PackageInfo, mocker: MockerFixture) -> None:
    """
    must return build packages
    """
    mocker.patch("pathlib.Path.iterdir", return_value=[Path("a.tar.xz"), Path("b.pkg.tar.xz")])
    assert package_info.packages_built() == [Path("b.pkg.tar.xz")]


def test_packages_depend_on(package_info: PackageInfo, package_ahriman: Package, package_python_schedule: Package,
                            mocker: MockerFixture) -> None:
    """
    must filter packages by depends list
    """
    mocker.patch("ahriman.core.repository.repository.Repository.packages",
                 return_value=[package_ahriman, package_python_schedule])
    assert package_info.packages_depend_on([package_ahriman], {"python-srcinfo"}) == [package_ahriman]


def test_packages_depend_on_empty(package_info: PackageInfo, package_ahriman: Package, package_python_schedule: Package,
                                  mocker: MockerFixture) -> None:
    """
    must return all packages in case if no filter is provided
    """
    mocker.patch("ahriman.core.repository.repository.Repository.packages",
                 return_value=[package_ahriman, package_python_schedule])
    assert package_info.packages_depend_on([package_ahriman, package_python_schedule], None) == \
        [package_ahriman, package_python_schedule]
