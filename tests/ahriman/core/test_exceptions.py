from ahriman.core.exceptions import BuildError, CalledProcessError


def test_from_process() -> None:
    """
    must correctly generate exception instance from subprocess
    """
    instance = BuildError.from_process("ahriman")(0, [], "out", "err")
    assert isinstance(instance, BuildError)
    assert instance.args == ("Package ahriman build failed,\nprocess stderr:\nerr\ncheck logs for details",)


def test_str() -> None:
    """
    must correctly transform CalledProcessError to string
    """
    instance = CalledProcessError(1, ["cmd"], "error")
    message = "Command '['cmd']' returned non-zero exit status 1.\nProcess stderr:\nerror"
    assert str(instance) == message
