from ahriman.models.worker import Worker


def test_post_init() -> None:
    """
    must read identifier from location if not set
    """
    assert Worker("http://localhost:8080").identifier == "localhost:8080"
    assert Worker("remote").identifier == ""  # not a valid url
    assert Worker("remote", identifier="id").identifier == "id"
