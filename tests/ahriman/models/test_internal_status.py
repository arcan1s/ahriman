from ahriman.models.internal_status import InternalStatus


def test_internal_status_from_json_view(internal_status: InternalStatus) -> None:
    """
    must construct same object from json
    """
    assert InternalStatus.from_json(internal_status.view()) == internal_status
