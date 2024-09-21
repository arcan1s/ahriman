import pytest

from io import StringIO
from pathlib import Path

from ahriman.core.alpm.pkgbuild_parser import PkgbuildParser
from ahriman.core.exceptions import PkgbuildParserError
from ahriman.models.pkgbuild_patch import PkgbuildPatch


def test_expand_array() -> None:
    """
    must correctly expand array
    """
    assert PkgbuildParser._expand_array(["${pkgbase}{", ",", "-libs", ",", "-fortran}"]) == [
        "${pkgbase}", "${pkgbase}-libs", "${pkgbase}-fortran"
    ]
    assert PkgbuildParser._expand_array(["first", "prefix{1", ",", "2", ",", "3}suffix", "last"]) == [
        "first", "prefix1suffix", "prefix2suffix", "prefix3suffix", "last"
    ]


def test_expand_array_no_comma() -> None:
    """
    must skip array extraction if there is no comma
    """
    assert PkgbuildParser._expand_array(["${pkgbase}{", "-libs", "-fortran}"]) == ["${pkgbase}{", "-libs", "-fortran}"]


def test_expand_array_short() -> None:
    """
    must skip array extraction if it is short
    """
    assert PkgbuildParser._expand_array(["${pkgbase}{", ","]) == ["${pkgbase}{", ","]


def test_expand_array_exception() -> None:
    """
    must raise exception if there is unclosed element
    """
    with pytest.raises(PkgbuildParserError):
        assert PkgbuildParser._expand_array(["${pkgbase}{", ",", "-libs"])


def test_parse_array() -> None:
    """
    must parse array
    """
    parser = PkgbuildParser(StringIO("var=(first second)"))
    assert list(parser.parse()) == [PkgbuildPatch("var", ["first", "second"])]


def test_parse_array_comment() -> None:
    """
    must parse array with comments inside
    """
    parser = PkgbuildParser(StringIO("""validpgpkeys=(
  'F3691687D867B81B51CE07D9BBE43771487328A9'  # bpiotrowski@archlinux.org
  '86CFFCA918CF3AF47147588051E8B148A9999C34'  # evangelos@foutrelis.com
  '13975A70E63C361C73AE69EF6EEB81F8981C74C7'  # richard.guenther@gmail.com
  'D3A93CAD751C2AF4F8C7AD516C35B99309B5FA62'  # Jakub Jelinek <jakub@redhat.com>
)"""))
    assert list(parser.parse()) == [PkgbuildPatch("validpgpkeys", [
        "F3691687D867B81B51CE07D9BBE43771487328A9",
        "86CFFCA918CF3AF47147588051E8B148A9999C34",
        "13975A70E63C361C73AE69EF6EEB81F8981C74C7",
        "D3A93CAD751C2AF4F8C7AD516C35B99309B5FA62",
    ])]


def test_parse_array_escaped() -> None:
    """
    must correctly process quoted brackets
    """
    parser = PkgbuildParser(StringIO("""var=(first "(" second)"""))
    assert list(parser.parse()) == [PkgbuildPatch("var", ["first", "(", "second"])]

    parser = PkgbuildParser(StringIO("""var=(first ")" second)"""))
    assert list(parser.parse()) == [PkgbuildPatch("var", ["first", ")", "second"])]

    parser = PkgbuildParser(StringIO("""var=(first ')' second)"""))
    assert list(parser.parse()) == [PkgbuildPatch("var", ["first", ")", "second"])]

    parser = PkgbuildParser(StringIO("""var=(first \\) second)"""))
    assert list(parser.parse()) == [PkgbuildPatch("var", ["first", ")", "second"])]


def test_parse_array_exception() -> None:
    """
    must raise exception if there is no closing bracket
    """
    parser = PkgbuildParser(StringIO("var=(first second"))
    with pytest.raises(PkgbuildParserError):
        assert list(parser.parse())


def test_parse_function() -> None:
    """
    must parse function
    """
    parser = PkgbuildParser(StringIO("var() { echo hello world } "))
    assert list(parser.parse()) == [PkgbuildPatch("var()", "{ echo hello world }")]


def test_parse_function_eof() -> None:
    """
    must parse function with "}" at the end of the file
    """
    parser = PkgbuildParser(StringIO("var() { echo hello world }"))
    assert list(parser.parse()) == [PkgbuildPatch("var()", "{ echo hello world }")]


def test_parse_function_spaces() -> None:
    """
    must parse function with spaces in declaration
    """
    parser = PkgbuildParser(StringIO("var ( ) { echo hello world } "))
    assert list(parser.parse()) == [PkgbuildPatch("var()", "{ echo hello world }")]


def test_parse_function_inner_shell() -> None:
    """
    must parse function with inner shell
    """
    parser = PkgbuildParser(StringIO("var ( ) { { echo hello world } } "))
    assert list(parser.parse()) == [PkgbuildPatch("var()", "{ { echo hello world } }")]


def test_parse_function_escaped() -> None:
    """
    must parse function with bracket in quotes
    """
    parser = PkgbuildParser(StringIO("""var ( ) { echo "hello world {" } """))
    assert list(parser.parse()) == [PkgbuildPatch("var()", """{ echo "hello world {" }""")]

    parser = PkgbuildParser(StringIO("""var ( ) { echo hello world "{" } """))
    assert list(parser.parse()) == [PkgbuildPatch("var()", """{ echo hello world "{" }""")]

    parser = PkgbuildParser(StringIO("""var ( ) { echo "hello world }" } """))
    assert list(parser.parse()) == [PkgbuildPatch("var()", """{ echo "hello world }" }""")]

    parser = PkgbuildParser(StringIO("""var ( ) { echo hello world "}" } """))
    assert list(parser.parse()) == [PkgbuildPatch("var()", """{ echo hello world "}" }""")]

    parser = PkgbuildParser(StringIO("""var ( ) { echo hello world '}' } """))
    assert list(parser.parse()) == [PkgbuildPatch("var()", """{ echo hello world '}' }""")]

    parser = PkgbuildParser(StringIO("""var ( ) { echo hello world \\} } """))
    assert list(parser.parse()) == [PkgbuildPatch("var()", """{ echo hello world \\} }""")]


def test_parse_function_exception() -> None:
    """
    must raise exception if no bracket found
    """
    parser = PkgbuildParser(StringIO("var() echo hello world } "))
    with pytest.raises(PkgbuildParserError):
        assert list(parser.parse())

    parser = PkgbuildParser(StringIO("var() { echo hello world"))
    with pytest.raises(PkgbuildParserError):
        assert list(parser.parse())


def test_parse_token_assignment() -> None:
    """
    must parse simple assignment
    """
    parser = PkgbuildParser(StringIO())
    assert next(parser._parse_token("var=value")) == PkgbuildPatch("var", "value")
    assert next(parser._parse_token("var=$value")) == PkgbuildPatch("var", "$value")
    assert next(parser._parse_token("var=${value}")) == PkgbuildPatch("var", "${value}")
    assert next(parser._parse_token("var=${value/-/_}")) == PkgbuildPatch("var", "${value/-/_}")


def test_parse_token_comment() -> None:
    """
    must correctly parse comment
    """
    parser = PkgbuildParser(StringIO("""first=1 # comment
    # comment line
    second=2
    #third=3
    """))
    assert list(parser.parse()) == [
        PkgbuildPatch("first", "1"),
        PkgbuildPatch("second", "2"),
    ]


def test_parse(resource_path_root: Path) -> None:
    """
    must parse complex file
    """
    pkgbuild = resource_path_root / "models" / "pkgbuild"
    with pkgbuild.open() as content:
        parser = PkgbuildParser(content)
        assert list(parser.parse()) == [
            PkgbuildPatch("var", "value"),
            PkgbuildPatch("var", "value"),
            PkgbuildPatch("var", "value with space"),
            PkgbuildPatch("var", "value"),
            PkgbuildPatch("var", "$ref"),
            PkgbuildPatch("var", "${ref}"),
            PkgbuildPatch("var", "$ref value"),
            PkgbuildPatch("var", "${ref}value"),
            PkgbuildPatch("var", "${ref/-/_}"),
            PkgbuildPatch("var", "${ref##.*}"),
            PkgbuildPatch("var", "${ref%%.*}"),
            PkgbuildPatch("array", ["first", "second", "third", "with space"]),
            PkgbuildPatch("array", ["single"]),
            PkgbuildPatch("array", ["$ref"]),
            PkgbuildPatch("array", ["first", "second", "third"]),
            PkgbuildPatch("array", ["first", "second", "third"]),
            PkgbuildPatch("array", ["first", "last"]),
            PkgbuildPatch("array", ["first", "1suffix", "2suffix", "last"]),
            PkgbuildPatch("array", ["first", "prefix1", "prefix2", "last"]),
            PkgbuildPatch("array", ["first", "prefix1suffix", "prefix2suffix", "last"]),
            PkgbuildPatch("array", ["first", "(", "second"]),
            PkgbuildPatch("array", ["first", ")", "second"]),
            PkgbuildPatch("array", ["first", "(", "second"]),
            PkgbuildPatch("array", ["first", ")", "second"]),
            PkgbuildPatch("function()", """{ single line }"""),
            PkgbuildPatch("function()", """{
    multi
    line
}"""),
            PkgbuildPatch("function()", """{
    c
    multi
    line
}"""),
            PkgbuildPatch("function()", """{
    # comment
    multi
    line
}"""),
            PkgbuildPatch("function()", """{
    body
}"""),
            PkgbuildPatch("function()", """{
    body
}"""),
            PkgbuildPatch("function_with-package-name()", """{ body }"""),
            PkgbuildPatch("function()", """{
    first
    { inner shell }
    last
}"""),
            PkgbuildPatch("function()", """{
    body "{" argument
}"""),
            PkgbuildPatch("function()", """{
    body "}" argument
}"""),
            PkgbuildPatch("function()", """{
    body '{' argument
}"""),
            PkgbuildPatch("function()", """{
    body '}' argument
}"""),
        ]
