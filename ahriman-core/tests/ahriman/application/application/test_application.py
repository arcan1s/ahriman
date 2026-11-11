from pathlib import Path
from pytest_mock import MockerFixture
from typing import Any
from unittest.mock import MagicMock, call as MockCall

from ahriman.application.application import Application
from ahriman.models.build_plan import BuildPlan, BuildPlanReason
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
    mocker.patch("ahriman.core.repository.repository.Repository.packages", return_value=[package_ahriman])
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")

    application.print_updates(BuildPlan().update([package_ahriman], BuildPlanReason.RegularUpdate), log_fn=print)
    print_mock.assert_called_once_with(verbose=True, log_fn=print, separator=": ")


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

    def get_package(name: str | Path, *args: Any, **kwargs: Any) -> Package:
        name = name if isinstance(name, str) else name.name
        return packages[name]

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
    package_aur_mock = mocker.patch("ahriman.models.package.Package.from_aur", side_effect=get_package)
    package_local_mock = mocker.patch("ahriman.models.package.Package.from_build", side_effect=get_package)
    packages_mock = mocker.patch("ahriman.application.application.Application._known_packages",
                                 return_value={"devtools", "python-build", "python-pytest"})
    status_client_mock = mocker.patch("ahriman.core.status.Client.set_unknown")

    plan = BuildPlan().update([package_ahriman], BuildPlanReason.RegularUpdate)
    result = application.with_dependencies(plan, process_dependencies=True)
    assert {package.base: package for package in result} == packages
    assert result.item(package_ahriman.base).requester is None
    assert result.item(package_python_schedule.base).requester == package_ahriman.base
    package_aur_mock.assert_has_calls([
        MockCall(package_python_schedule.base, package_ahriman.packager, include_provides=True),
        MockCall("python-installer", package_ahriman.packager, include_provides=True),
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

    plan = BuildPlan()
    plan.add(package_ahriman, BuildPlanReason.RegularUpdate)
    assert application.with_dependencies(plan, process_dependencies=True) is plan
    assert plan.packages == [package_ahriman]


def test_with_dependencies_skip(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must skip processing of dependencies
    """
    packages_mock = mocker.patch("ahriman.application.application.Application._known_packages")

    plan = BuildPlan().update([package_ahriman], BuildPlanReason.RegularUpdate)
    assert application.with_dependencies(plan, process_dependencies=False).packages == [package_ahriman]
    packages_mock.assert_not_called()

    assert not application.with_dependencies(BuildPlan(), process_dependencies=True)
    packages_mock.assert_not_called()
