from ahriman.models.log_record_id import LogRecordId


def test_init() -> None:
    """
    must correctly assign proces identifier if not set
    """
    assert LogRecordId("1", "2").process_id == LogRecordId.DEFAULT_PROCESS_ID
    assert LogRecordId("1", "2", "3").process_id == "3"
