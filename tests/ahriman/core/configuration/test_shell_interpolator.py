import os

from ahriman.core.configuration.shell_interpolator import ShellInterpolator


def test_before_get() -> None:
    """
    must correctly extract environment variables
    """
    interpolator = ShellInterpolator()

    assert interpolator.before_get({}, "", "", "value", {}) == "value"
    assert interpolator.before_get({}, "", "", "$value", {}) == "$value"
    assert interpolator.before_get({}, "", "", "$HOME", {}) == os.environ["HOME"]
    assert interpolator.before_get({}, "", "", "$$HOME", {}) == "$HOME"
