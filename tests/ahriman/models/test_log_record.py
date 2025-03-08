from ahriman.models.log_record import LogRecord
from ahriman.models.log_record_id import LogRecordId


def test_log_record_from_json_view() -> None:
    """
    must construct same object from json
    """
    log_record = LogRecord(LogRecordId("base", "version"), 0, "message")
    assert LogRecord.from_json(log_record.log_record_id.package_base, log_record.view()) == log_record

    log_record = LogRecord(LogRecordId("base", "version", "process_id"), 0, "message")
    assert LogRecord.from_json(log_record.log_record_id.package_base, log_record.view()) == log_record
