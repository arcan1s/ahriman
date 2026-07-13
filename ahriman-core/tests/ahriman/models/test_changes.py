from ahriman.models.changes import Changes


def test_changes_from_json_view() -> None:
    """
    must construct same object from json
    """
    changes = Changes()
    assert Changes.from_json(changes.view()) == changes

    changes = Changes("sha")
    assert Changes.from_json(changes.view()) == changes

    changes = Changes("sha", "change")
    assert Changes.from_json(changes.view()) == changes
