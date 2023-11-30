from ahriman.models.changes import Changes


def test_is_empty() -> None:
    """
    must check if changes are empty
    """
    assert Changes().is_empty
    assert Changes("sha").is_empty

    assert not Changes("sha", "change").is_empty
    assert not Changes(None, "change").is_empty  # well, ok


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
