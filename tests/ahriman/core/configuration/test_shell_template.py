from ahriman.core.configuration.shell_template import ShellTemplate


def test_shell_template_braceidpattern() -> None:
    """
    must match colons in braces
    """
    assert ShellTemplate("$k:value").get_identifiers() == ["k"]
    assert ShellTemplate("${k:value}").get_identifiers() == ["k:value"]


def test_remove_back() -> None:
    """
    must remove substring from the back
    """
    assert ShellTemplate("${k%removeme}").shell_substitute({"k": "please removeme"}) == "please "
    assert ShellTemplate("${k%removeme*}").shell_substitute({"k": "please removeme removeme"}) == "please removeme "
    assert ShellTemplate("${k%removem?}").shell_substitute({"k": "please removeme removeme"}) == "please removeme "

    assert ShellTemplate("${k%%removeme}").shell_substitute({"k": "please removeme removeme"}) == "please removeme "
    assert ShellTemplate("${k%%removeme*}").shell_substitute({"k": "please removeme removeme"}) == "please "
    assert ShellTemplate("${k%%removem?}").shell_substitute({"k": "please removeme removeme"}) == "please removeme "

    assert ShellTemplate("${k%removeme}").shell_substitute({}) == "${k%removeme}"
    assert ShellTemplate("${k%%removeme}").shell_substitute({}) == "${k%%removeme}"

    assert ShellTemplate("${k%r3m0v3m3}").shell_substitute({"k": "please removeme"}) == "please removeme"
    assert ShellTemplate("${k%%r3m0v3m3}").shell_substitute({"k": "please removeme"}) == "please removeme"


def test_remove_front() -> None:
    """
    must remove substring from the front
    """
    assert ShellTemplate("${k#removeme}").shell_substitute({"k": "removeme please"}) == " please"
    assert ShellTemplate("${k#*removeme}").shell_substitute({"k": "removeme removeme please"}) == " removeme please"
    assert ShellTemplate("${k#removem?}").shell_substitute({"k": "removeme removeme please"}) == " removeme please"

    assert ShellTemplate("${k##removeme}").shell_substitute({"k": "removeme removeme please"}) == " removeme please"
    assert ShellTemplate("${k##*removeme}").shell_substitute({"k": "removeme removeme please"}) == " please"
    assert ShellTemplate("${k##removem?}").shell_substitute({"k": "removeme removeme please"}) == " removeme please"

    assert ShellTemplate("${k#removeme}").shell_substitute({}) == "${k#removeme}"
    assert ShellTemplate("${k##removeme}").shell_substitute({}) == "${k##removeme}"

    assert ShellTemplate("${k#r3m0v3m3}").shell_substitute({"k": "removeme please"}) == "removeme please"
    assert ShellTemplate("${k##r3m0v3m3}").shell_substitute({"k": "removeme please"}) == "removeme please"


def test_replace() -> None:
    """
    must perform regular replacement
    """
    assert ShellTemplate("${k/in/out}").shell_substitute({"k": "in replace in"}) == "out replace in"
    assert ShellTemplate("${k/in*/out}").shell_substitute({"k": "in replace in"}) == "out"
    assert ShellTemplate("${k/*in/out}").shell_substitute({"k": "in replace in replace"}) == "out replace"
    assert ShellTemplate("${k/i?/out}").shell_substitute({"k": "in replace in"}) == "out replace in"

    assert ShellTemplate("${k//in/out}").shell_substitute({"k": "in replace in"}) == "out replace out"
    assert ShellTemplate("${k//in*/out}").shell_substitute({"k": "in replace in"}) == "out"
    assert ShellTemplate("${k//*in/out}").shell_substitute({"k": "in replace in replace"}) == "out replace"
    assert ShellTemplate("${k//i?/out}").shell_substitute({"k": "in replace in replace"}) == "out replace out replace"

    assert ShellTemplate("${k/in/out}").shell_substitute({}) == "${k/in/out}"
    assert ShellTemplate("${k//in/out}").shell_substitute({}) == "${k//in/out}"


def test_replace_back() -> None:
    """
    must replace substring from the back
    """
    assert ShellTemplate("${k/%in/out}").shell_substitute({"k": "in replace in"}) == "in replace out"
    assert ShellTemplate("${k/%in/out}").shell_substitute({"k": "in replace in "}) == "in replace in "


def test_replace_front() -> None:
    """
    must replace substring from the front
    """
    assert ShellTemplate("${k/#in/out}").shell_substitute({"k": "in replace in"}) == "out replace in"
    assert ShellTemplate("${k/#in/out}").shell_substitute({"k": " in replace in"}) == " in replace in"
