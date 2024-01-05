from unittest.mock import MagicMock

from ahriman.core.configuration import Configuration
from ahriman.core.report import ReportTrigger
from ahriman.core.triggers import Trigger
from ahriman.models.result import Result


def test_architecture(trigger: Trigger) -> None:
    """
    must return repository architecture for backward compatibility
    """
    assert trigger.architecture == trigger.repository_id.architecture


def test_configuration_schema(configuration: Configuration) -> None:
    """
    must return used configuration schema
    """
    section = "console"
    configuration.set_option("report", "target", section)
    _, repository_id = configuration.check_loaded()

    expected = {section: ReportTrigger.CONFIGURATION_SCHEMA[section]}
    assert ReportTrigger.configuration_schema(repository_id, configuration) == expected


def test_configuration_schema_no_section(configuration: Configuration) -> None:
    """
    must return nothing in case if section doesn't exist
    """
    section = "abracadabra"
    configuration.set_option("report", "target", section)
    _, repository_id = configuration.check_loaded()

    assert ReportTrigger.configuration_schema(repository_id, configuration) == {}


def test_configuration_schema_no_schema(configuration: Configuration) -> None:
    """
    must return nothing in case if schema doesn't exist
    """
    section = "abracadabra"
    configuration.set_option("report", "target", section)
    configuration.set_option(section, "key", "value")
    _, repository_id = configuration.check_loaded()

    assert ReportTrigger.configuration_schema(repository_id, configuration) == {}


def test_configuration_schema_empty(configuration: Configuration) -> None:
    """
    must return default schema if no configuration set
    """
    _, repository_id = configuration.check_loaded()
    assert ReportTrigger.configuration_schema(repository_id, None) == ReportTrigger.CONFIGURATION_SCHEMA


def test_configuration_schema_variables() -> None:
    """
    must return empty schema
    """
    assert Trigger.CONFIGURATION_SCHEMA == {}
    assert Trigger.CONFIGURATION_SCHEMA_FALLBACK is None


def test_configuration_sections(configuration: Configuration) -> None:
    """
    must return empty section list
    """
    assert Trigger.configuration_sections(configuration) == []


def test_on_result(trigger: Trigger) -> None:
    """
    must pass execution nto run method
    """
    trigger.on_result(Result(), [])


def test_on_result_run(trigger: Trigger) -> None:
    """
    must fall back to run method if it exists
    """
    run_mock = MagicMock()
    setattr(trigger, "run", run_mock)

    trigger.on_result(Result(), [])
    run_mock.assert_called_once_with(Result(), [])


def test_on_start(trigger: Trigger) -> None:
    """
    must do nothing for not implemented method on_start
    """
    trigger.on_start()


def test_on_stop(trigger: Trigger) -> None:
    """
    must do nothing for not implemented method on_stop
    """
    trigger.on_stop()
