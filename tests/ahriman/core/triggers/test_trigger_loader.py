import pytest

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import ExtensionError
from ahriman.core.report import ReportTrigger
from ahriman.core.triggers import TriggerLoader
from ahriman.models.package import Package
from ahriman.models.result import Result


def test_known_triggers(configuration: Configuration) -> None:
    """
    must return used triggers
    """
    configuration.set_option("build", "triggers_known", "a b c")
    assert TriggerLoader.known_triggers(configuration) == ["a", "b", "c"]

    configuration.remove_option("build", "triggers_known")
    assert TriggerLoader.known_triggers(configuration) == []


def test_selected_triggers(configuration: Configuration) -> None:
    """
    must return used triggers
    """
    configuration.set_option("build", "triggers", "a b c")
    assert TriggerLoader.selected_triggers(configuration) == ["a", "b", "c"]

    configuration.remove_option("build", "triggers")
    assert TriggerLoader.selected_triggers(configuration) == []


def test_load_trigger(trigger_loader: TriggerLoader, configuration: Configuration) -> None:
    """
    must load trigger
    """
    loaded = trigger_loader.load_trigger("ahriman.core.report.ReportTrigger", "x86_64", configuration)
    assert loaded
    assert isinstance(loaded, ReportTrigger)


def test_load_trigger_package_error_on_creation(trigger_loader: TriggerLoader, configuration: Configuration,
                                                mocker: MockerFixture) -> None:
    """
    must raise InvalidException on trigger initialization if any exception is thrown
    """
    mocker.patch("ahriman.core.triggers.trigger.Trigger.__init__", side_effect=Exception())
    _, repository_id = configuration.check_loaded()

    with pytest.raises(ExtensionError):
        trigger_loader.load_trigger("ahriman.core.report.ReportTrigger", repository_id, configuration)


def test_load_trigger_class_package(trigger_loader: TriggerLoader) -> None:
    """
    must load trigger class from package
    """
    assert trigger_loader.load_trigger_class("ahriman.core.report.ReportTrigger") == ReportTrigger


def test_load_trigger_class_package_invalid_import(trigger_loader: TriggerLoader, mocker: MockerFixture) -> None:
    """
    must raise InvalidExtension on invalid import
    """
    mocker.patch("importlib.import_module", side_effect=ModuleNotFoundError())
    with pytest.raises(ExtensionError):
        trigger_loader.load_trigger_class("random.module")


def test_load_trigger_class_package_not_trigger(trigger_loader: TriggerLoader) -> None:
    """
    must raise InvalidExtension if imported module is not a type
    """
    with pytest.raises(ExtensionError):
        trigger_loader.load_trigger_class("ahriman.core.util.check_output")


def test_load_trigger_class_package_is_not_trigger(trigger_loader: TriggerLoader) -> None:
    """
    must raise InvalidExtension if loaded class is not a trigger
    """
    with pytest.raises(ExtensionError):
        trigger_loader.load_trigger_class("ahriman.core.sign.gpg.GPG")


def test_load_trigger_class_path(trigger_loader: TriggerLoader, resource_path_root: Path) -> None:
    """
    must load trigger class from path
    """
    path = resource_path_root.parent.parent / "src" / "ahriman" / "core" / "report" / "__init__.py"
    assert trigger_loader.load_trigger_class(f"{path}.ReportTrigger") == ReportTrigger


def test_load_trigger_class_path_directory(trigger_loader: TriggerLoader, resource_path_root: Path) -> None:
    """
    must raise InvalidExtension if provided import path is directory
    """
    path = resource_path_root.parent.parent / "src" / "ahriman" / "core" / "report"
    with pytest.raises(ExtensionError):
        trigger_loader.load_trigger_class(f"{path}.ReportTrigger")


def test_load_trigger_class_path_not_found(trigger_loader: TriggerLoader) -> None:
    """
    must raise InvalidExtension if file cannot be found
    """
    with pytest.raises(ExtensionError):
        trigger_loader.load_trigger_class("/some/random/path.py.SomeRandomModule")


def test_on_result(trigger_loader: TriggerLoader, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run triggers
    """
    upload_mock = mocker.patch("ahriman.core.upload.UploadTrigger.on_result")
    report_mock = mocker.patch("ahriman.core.report.ReportTrigger.on_result")

    trigger_loader.on_result(Result(), [package_ahriman])
    report_mock.assert_called_once_with(Result(), [package_ahriman])
    upload_mock.assert_called_once_with(Result(), [package_ahriman])


def test_on_result_exception(trigger_loader: TriggerLoader, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress exception during trigger run
    """
    upload_mock = mocker.patch("ahriman.core.upload.UploadTrigger.on_result", side_effect=Exception())
    report_mock = mocker.patch("ahriman.core.report.ReportTrigger.on_result")
    log_mock = mocker.patch("logging.Logger.exception")

    trigger_loader.on_result(Result(), [package_ahriman])
    report_mock.assert_called_once_with(Result(), [package_ahriman])
    upload_mock.assert_called_once_with(Result(), [package_ahriman])
    log_mock.assert_called_once()


def test_on_start(trigger_loader: TriggerLoader, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run triggers on start
    """
    upload_mock = mocker.patch("ahriman.core.upload.UploadTrigger.on_start")
    report_mock = mocker.patch("ahriman.core.report.ReportTrigger.on_start")

    trigger_loader.on_start()
    assert trigger_loader._on_stop_requested
    report_mock.assert_called_once_with()
    upload_mock.assert_called_once_with()


def test_on_stop_with_on_start(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must call on_stop on exit if on_start was called
    """
    mocker.patch("ahriman.core.upload.UploadTrigger.on_start")
    mocker.patch("ahriman.core.report.ReportTrigger.on_start")
    on_stop_mock = mocker.patch("ahriman.core.triggers.trigger_loader.TriggerLoader.on_stop")
    _, repository_id = configuration.check_loaded()

    trigger_loader = TriggerLoader.load(repository_id, configuration)
    trigger_loader.on_start()
    del trigger_loader
    on_stop_mock.assert_called_once_with()


def test_on_stop_without_on_start(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must call not on_stop on exit if on_start wasn't called
    """
    on_stop_mock = mocker.patch("ahriman.core.triggers.trigger_loader.TriggerLoader.on_stop")
    _, repository_id = configuration.check_loaded()

    trigger_loader = TriggerLoader.load(repository_id, configuration)
    del trigger_loader
    on_stop_mock.assert_not_called()


def test_on_stop(trigger_loader: TriggerLoader, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run triggers on stop
    """
    upload_mock = mocker.patch("ahriman.core.upload.UploadTrigger.on_stop")
    report_mock = mocker.patch("ahriman.core.report.ReportTrigger.on_stop")

    trigger_loader.on_stop()
    report_mock.assert_called_once_with()
    upload_mock.assert_called_once_with()
