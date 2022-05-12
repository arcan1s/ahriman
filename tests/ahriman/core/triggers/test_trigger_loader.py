import pytest

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.exceptions import InvalidExtension
from ahriman.core.triggers import TriggerLoader
from ahriman.models.package import Package
from ahriman.models.result import Result


def test_load_trigger_package(trigger_loader: TriggerLoader) -> None:
    """
    must load trigger from package
    """
    assert trigger_loader._load_trigger("ahriman.core.report.ReportTrigger")


def test_load_trigger_package_invalid_import(trigger_loader: TriggerLoader, mocker: MockerFixture) -> None:
    """
    must raise InvalidExtension on invalid import
    """
    mocker.patch("ahriman.core.triggers.trigger_loader.importlib.import_module", side_effect=ModuleNotFoundError())
    with pytest.raises(InvalidExtension):
        trigger_loader._load_trigger("random.module")


def test_load_trigger_package_not_trigger(trigger_loader: TriggerLoader) -> None:
    """
    must raise InvalidExtension if imported module is not a type
    """
    with pytest.raises(InvalidExtension):
        trigger_loader._load_trigger("ahriman.core.util.check_output")


def test_load_trigger_package_error_on_creation(trigger_loader: TriggerLoader, mocker: MockerFixture) -> None:
    """
    must raise InvalidException on trigger initialization if any exception is thrown
    """
    mocker.patch("ahriman.core.triggers.trigger.Trigger.__init__", side_effect=Exception())
    with pytest.raises(InvalidExtension):
        trigger_loader._load_trigger("ahriman.core.report.ReportTrigger")


def test_load_trigger_package_is_not_trigger(trigger_loader: TriggerLoader) -> None:
    """
    must raise InvalidExtension if loaded class is not a trigger
    """
    with pytest.raises(InvalidExtension):
        trigger_loader._load_trigger("ahriman.core.sign.gpg.GPG")


def test_load_trigger_path(trigger_loader: TriggerLoader, resource_path_root: Path) -> None:
    """
    must load trigger from path
    """
    path = resource_path_root.parent.parent / "src" / "ahriman" / "core" / "report" / "report_trigger.py"
    assert trigger_loader._load_trigger(f"{path}.ReportTrigger")


def test_load_trigger_path_directory(trigger_loader: TriggerLoader, resource_path_root: Path) -> None:
    """
    must raise InvalidExtension if provided import path is directory
    """
    path = resource_path_root.parent.parent / "src" / "ahriman" / "core" / "report"
    with pytest.raises(InvalidExtension):
        trigger_loader._load_trigger(f"{path}.ReportTrigger")


def test_load_trigger_path_not_found(trigger_loader: TriggerLoader) -> None:
    """
    must raise InvalidExtension if file cannot be found
    """
    with pytest.raises(InvalidExtension):
        trigger_loader._load_trigger("/some/random/path.py.SomeRandomModule")


def test_process(trigger_loader: TriggerLoader, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run triggers
    """
    upload_mock = mocker.patch("ahriman.core.upload.UploadTrigger.run")
    report_mock = mocker.patch("ahriman.core.report.ReportTrigger.run")

    trigger_loader.process(Result(), [package_ahriman])
    report_mock.assert_called_once_with(Result(), [package_ahriman])
    upload_mock.assert_called_once_with(Result(), [package_ahriman])


def test_process_exception(trigger_loader: TriggerLoader, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress exception during trigger run
    """
    upload_mock = mocker.patch("ahriman.core.upload.UploadTrigger.run", side_effect=Exception())
    report_mock = mocker.patch("ahriman.core.report.ReportTrigger.run")
    log_mock = mocker.patch("logging.Logger.exception")

    trigger_loader.process(Result(), [package_ahriman])
    report_mock.assert_called_once_with(Result(), [package_ahriman])
    upload_mock.assert_called_once_with(Result(), [package_ahriman])
    log_mock.assert_called_once()
