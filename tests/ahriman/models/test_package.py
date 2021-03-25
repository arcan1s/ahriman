from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


def test_git_url(package_ahriman: Package) -> None:
    """
    must generate valid git url
    """
    assert package_ahriman.git_url.endswith(".git")
    assert package_ahriman.git_url.startswith(package_ahriman.aur_url)
    assert package_ahriman.base in package_ahriman.git_url


def test_is_single_package_false(package_python_schedule: Package) -> None:
    """
    python-schedule must not be single package
    """
    assert not package_python_schedule.is_single_package


def test_is_single_package_true(package_ahriman: Package) -> None:
    """
    ahriman must be single package
    """
    assert package_ahriman.is_single_package


def test_is_vcs_false(package_ahriman: Package) -> None:
    """
    ahriman must not be VCS package
    """
    assert not package_ahriman.is_vcs


def test_is_vcs_true(package_tpacpi_bat_git: Package) -> None:
    """
    tpacpi-bat-git must be VCS package
    """
    assert package_tpacpi_bat_git.is_vcs


def test_web_url(package_ahriman: Package) -> None:
    """
    must generate valid web url
    """
    assert package_ahriman.web_url.startswith(package_ahriman.aur_url)
    assert package_ahriman.base in package_ahriman.web_url


def test_from_json_view_1(package_ahriman: Package) -> None:
    """
    must construct same object from json
    """
    assert Package.from_json(package_ahriman.view()) == package_ahriman


def test_from_json_view_2(package_python_schedule: Package) -> None:
    """
    must construct same object from json
    """
    assert Package.from_json(package_python_schedule.view()) == package_python_schedule


def test_from_json_view_3(package_tpacpi_bat_git: Package) -> None:
    """
    must construct same object from json
    """
    assert Package.from_json(package_tpacpi_bat_git.view()) == package_tpacpi_bat_git


def test_dependencies_with_version(mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must load correct list of dependencies with version
    """
    srcinfo = (resource_path_root / "models" / "package_yay_srcinfo").read_text()

    mocker.patch("pathlib.Path.read_text", return_value=srcinfo)

    assert Package.dependencies(Path("path")) == {"git", "go", "pacman"}


def test_actual_version(package_ahriman: Package, repository_paths: RepositoryPaths) -> None:
    """
    must return same actual_version as version is
    """
    assert package_ahriman.actual_version(repository_paths) == package_ahriman.version


def test_actual_version_vcs(package_tpacpi_bat_git: Package, repository_paths: RepositoryPaths,
                            mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must return valid actual_version for VCS package
    """
    srcinfo = (resource_path_root / "models" / "package_tpacpi-bat-git_srcinfo").read_text()

    mocker.patch("ahriman.models.package.Package._check_output", return_value=srcinfo)
    mocker.patch("ahriman.core.build_tools.task.Task.fetch", return_value=None)

    assert package_tpacpi_bat_git.actual_version(repository_paths) == "3.1.r13.g4959b52-1"


def test_is_outdated_false(package_ahriman: Package, repository_paths: RepositoryPaths) -> None:
    """
    must be not outdated for the same package
    """
    assert not package_ahriman.is_outdated(package_ahriman, repository_paths)


def test_is_outdated_true(package_ahriman: Package, repository_paths: RepositoryPaths) -> None:
    """
    must be outdated for the new version
    """
    other = Package.from_json(package_ahriman.view())
    other.version = other.version.replace("-1", "-2")

    assert package_ahriman.is_outdated(other, repository_paths)
