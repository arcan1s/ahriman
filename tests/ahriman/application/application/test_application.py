from pytest_mock import MockerFixture
from unittest.mock import MagicMock, call as MockCall

from ahriman.application.application import Application
from ahriman.core.tree import Leaf, Tree
from ahriman.models.package import Package
from ahriman.models.result import Result


def test_known_packages(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return not empty list of known packages
    """
    mocker.patch("ahriman.core.repository.repository.Repository.packages", return_value=[package_ahriman])
    packages = application._known_packages()
    assert len(packages) > 1
    assert package_ahriman.base in packages


def test_on_result(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must call on_result trigger function
    """
    mocker.patch("ahriman.core.repository.Repository.packages", return_value=[package_ahriman])
    triggers_mock = mocker.patch("ahriman.core.triggers.TriggerLoader.on_result")

    application.on_result(Result())
    triggers_mock.assert_called_once_with(Result(), [package_ahriman])


def test_on_start(application: Application, mocker: MockerFixture) -> None:
    """
    must call on_start trigger function
    """
    triggers_mock = mocker.patch("ahriman.core.triggers.TriggerLoader.on_start")

    application.on_start()
    triggers_mock.assert_called_once_with()


def test_on_stop(application: Application, mocker: MockerFixture) -> None:
    """
    must call on_stop trigger function
    """
    triggers_mock = mocker.patch("ahriman.core.triggers.TriggerLoader.on_stop")

    application.on_stop()
    triggers_mock.assert_called_once_with()


def test_print_updates(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must print updates
    """
    tree = Tree([Leaf(package_ahriman)])
    mocker.patch("ahriman.core.repository.repository.Repository.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.core.tree.Tree.resolve", return_value=tree.levels())
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")

    application.print_updates([package_ahriman], log_fn=print)
    print_mock.assert_called_once_with(verbose=True, log_fn=print, separator=" -> ")


def test_with_dependencies(application: Application, package_ahriman: Package, package_python_schedule: Package,
                           mocker: MockerFixture) -> None:
    """
    must append list of missing dependencies
    """
    def create_package_mock(package_base) -> MagicMock:
        mock = MagicMock()
        mock.base = package_base
        mock.depends_build = []
        mock.packages_full = [package_base]
        return mock

    package_python_schedule.packages = {
        package_python_schedule.base: package_python_schedule.packages[package_python_schedule.base]
    }
    package_ahriman.packages[package_ahriman.base].depends = ["devtools", "python", package_python_schedule.base]
    package_ahriman.packages[package_ahriman.base].make_depends = ["python-build", "python-installer"]

    packages = {
        package_ahriman.base: package_ahriman,
        package_python_schedule.base: package_python_schedule,
        "python": create_package_mock("python"),
        "python-installer": create_package_mock("python-installer"),
    }

    mocker.patch("pathlib.Path.is_dir", autospec=True, side_effect=lambda p: p.name == "python")
    package_aur_mock = mocker.patch("ahriman.models.package.Package.from_aur",
                                    side_effect=lambda *args: packages[args[0]])
    package_local_mock = mocker.patch("ahriman.models.package.Package.from_build",
                                      side_effect=lambda *args: packages[args[0].name])
    packages_mock = mocker.patch("ahriman.application.application.Application._known_packages",
                                 return_value={"devtools", "python-build", "python-pytest"})
    status_client_mock = mocker.patch("ahriman.core.status.Client.set_unknown")

    result = application.with_dependencies([package_ahriman], process_dependencies=True)
    assert {package.base: package for package in result} == packages
    package_aur_mock.assert_has_calls([
        MockCall(package_python_schedule.base, package_ahriman.packager),
        MockCall("python-installer", package_ahriman.packager),
    ], any_order=True)
    package_local_mock.assert_has_calls([
        MockCall(application.repository.paths.cache_for("python"), "x86_64", package_ahriman.packager),
    ], any_order=True)
    packages_mock.assert_called_once_with()

    status_client_mock.assert_has_calls([
        MockCall(package_python_schedule),
        MockCall(packages["python"]),
        MockCall(packages["python-installer"]),
    ], any_order=True)


def test_with_dependencies_exception(application: Application, package_ahriman: Package,
                                     package_python_schedule: Package, mocker: MockerFixture) -> None:
    """
    must skip packages if exception occurs
    """
    def create_package_mock(package_base) -> MagicMock:
        mock = MagicMock()
        mock.base = package_base
        mock.depends_build = []
        mock.packages_full = [package_base]
        return mock

    package_python_schedule.packages = {
        package_python_schedule.base: package_python_schedule.packages[package_python_schedule.base]
    }
    package_ahriman.packages[package_ahriman.base].depends = ["devtools", "python", package_python_schedule.base]
    package_ahriman.packages[package_ahriman.base].make_depends = ["python-build", "python-installer"]

    packages = {
        package_ahriman.base: package_ahriman,
        package_python_schedule.base: package_python_schedule,
        "python": create_package_mock("python"),
        "python-installer": create_package_mock("python-installer"),
    }

    mocker.patch("pathlib.Path.is_dir", autospec=True, side_effect=lambda p: p.name == "python")
    mocker.patch("ahriman.models.package.Package.from_aur", side_effect=lambda *args: packages[args[0]])
    mocker.patch("ahriman.models.package.Package.from_build", side_effect=Exception)
    mocker.patch("ahriman.application.application.Application._known_packages",
                 return_value={"devtools", "python-build", "python-pytest"})

    assert not application.with_dependencies([package_ahriman], process_dependencies=True)


def test_with_dependencies_skip(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must skip processing of dependencies
    """
    packages_mock = mocker.patch("ahriman.application.application.Application._known_packages")

    assert application.with_dependencies([package_ahriman], process_dependencies=False) == [package_ahriman]
    packages_mock.assert_not_called()

    assert application.with_dependencies([], process_dependencies=True) == []
    packages_mock.assert_not_called()
