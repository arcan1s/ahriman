from ahriman.models.worker import Worker


def test_post_init() -> None:
    """
    must read identifier from location if not set
    """
    assert Worker("http://localhost:8080").identifier == "localhost:8080"
    assert Worker("remote").identifier == ""  # not a valid url
    assert Worker("remote", identifier="id").identifier == "id"


def test_view() -> None:
    """
    must generate json view
    """
    worker = Worker("address")
    assert worker.view() == {"address": worker.address, "identifier": worker.identifier}

    worker = Worker("http://localhost:8080")
    assert worker.view() == {"address": worker.address, "identifier": worker.identifier}

    worker = Worker("http://localhost:8080", identifier="abc")
    assert worker.view() == {"address": worker.address, "identifier": worker.identifier}
