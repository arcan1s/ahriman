import logging

from ahriman.core.log.log_context import LogContext


def test_get() -> None:
    """
    must get context variable value
    """
    token = LogContext.set("package_id", "value")
    assert LogContext.get("package_id") == "value"
    LogContext.reset("package_id", token)


def test_get_empty() -> None:
    """
    must return None when context variable is unknown or not set
    """
    assert LogContext.get("package_id") is None
    assert LogContext.get("random") is None


def test_log_record_factory() -> None:
    """
    must inject all registered context variables into log records
    """
    package_token = LogContext.set("package_id", "package")

    record = logging.makeLogRecord({})
    assert record.package_id == "package"

    LogContext.reset("package_id", package_token)


def test_log_record_factory_empty() -> None:
    """
    must not inject context variable when value is None
    """
    record = logging.makeLogRecord({})
    assert not hasattr(record, "package_id")


def test_register() -> None:
    """
    must register a context variable
    """
    variable = LogContext.register("random")

    assert "random" in LogContext._context
    assert LogContext._context["random"] is variable

    del LogContext._context["random"]


def test_reset() -> None:
    """
    must reset context variable so it is no longer injected
    """
    token = LogContext.set("package_id", "value")
    LogContext.reset("package_id", token)

    record = logging.makeLogRecord({})
    assert not hasattr(record, "package_id")


def test_set() -> None:
    """
    must set context variable and inject it into log records
    """
    token = LogContext.set("package_id", "value")

    record = logging.makeLogRecord({})
    assert record.package_id == "value"

    LogContext.reset("package_id", token)
