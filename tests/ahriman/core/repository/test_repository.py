from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.repository.repository import Repository
from ahriman.models.package import Package


def test_packages(package_ahriman: Package, package_python_schedule: Package,
                  repository: Repository, mocker: MockerFixture) -> None:
    """
    must return all packages grouped by package base
    """
    single_packages = [
        Package(base=package_python_schedule.base,
                version=package_python_schedule.version,
                aur_url=package_python_schedule.aur_url,
                packages={package: props})
        for package, props in package_python_schedule.packages.items()
    ] + [package_ahriman]

    mocker.patch("pathlib.Path.iterdir",
                 return_value=[Path("a.pkg.tar.xz"), Path("b.pkg.tar.xz"), Path("c.pkg.tar.xz")])
    mocker.patch("ahriman.models.package.Package.load", side_effect=single_packages)

    packages = repository.packages()
    assert len(packages) == 2
    assert {package.base for package in packages} == {package_ahriman.base, package_python_schedule.base}

    archives = sum([list(package.packages.keys()) for package in packages], start=[])
    assert len(archives) == 3
    expected = set(package_ahriman.packages.keys())
    expected.update(package_python_schedule.packages.keys())
    assert set(archives) == expected
