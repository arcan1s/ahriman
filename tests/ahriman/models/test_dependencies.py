from ahriman.models.dependencies import Dependencies


def test_from_json_view() -> None:
    """
    must construct and serialize dependencies to json
    """
    dependencies = Dependencies({"/usr/bin/python3": ["python"]})
    assert Dependencies.from_json(dependencies.view()) == dependencies
