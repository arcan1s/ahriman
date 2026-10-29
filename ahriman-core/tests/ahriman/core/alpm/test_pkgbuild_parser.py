import pytest

from io import BytesIO
from pathlib import Path

from ahriman.core.alpm.pkgbuild_parser import PkgbuildParser
from ahriman.core.exceptions import PkgbuildParserError
from ahriman.models.pkgbuild_patch import PkgbuildPatch


def test_expand_array() -> None:
    """
    must correctly expand array
    """
    parser = PkgbuildParser(BytesIO(b"array=(prefix{only}suffix)"))
    assert list(parser.parse()) == [PkgbuildPatch("array", ["prefix{only}suffix"])]

    parser = PkgbuildParser(BytesIO(b"array=(prefix{first,second}suffix)"))
    assert list(parser.parse()) == [PkgbuildPatch("array", ["prefixfirstsuffix", "prefixsecondsuffix"])]

    parser = PkgbuildParser(BytesIO(br"array=(prefix{first\,second,third}suffix)"))
    assert list(parser.parse()) == [PkgbuildPatch("array", ["prefixfirst,secondsuffix", "prefixthirdsuffix"])]

    parser = PkgbuildParser(BytesIO(b"""array=("prefix{first,second}suffix")"""))
    assert list(parser.parse()) == [PkgbuildPatch("array", ["prefix{first,second}suffix"])]

    parser = PkgbuildParser(BytesIO(b"""array=(x"{a,b}" x'{a,b}' "{x,y}"{a,b})"""))
    assert list(parser) == [PkgbuildPatch("array", ["x{a,b}", "x{a,b}", "{x,y}a", "{x,y}b"])]

    parser = PkgbuildParser(BytesIO(b"""array=(${v:-a,b}suffix ${v:-a,b}{,.sig} $(echo '{a,b}')suffix)"""))
    assert list(parser) == [PkgbuildPatch("array", [
        "${v:-a,b}suffix", "${v:-a,b}", "${v:-a,b}.sig", "$(echo '{a,b}')suffix",
    ])]


def test_parse_append_array() -> None:
    """
    must retain original array elements when appending and iterating again
    """
    parser = PkgbuildParser(BytesIO(
        b"source=(base.patch)\nsource+=(extra.patch)\nsource+=(last.patch)\nsource=(reset.patch)\nsource+=(extra.patch)"
    ))
    expected = [
        PkgbuildPatch("source", ["base.patch"]),
        PkgbuildPatch("source", ["base.patch", "extra.patch"]),
        PkgbuildPatch("source", ["base.patch", "extra.patch", "last.patch"]),
        PkgbuildPatch("source", ["reset.patch"]),
        PkgbuildPatch("source", ["reset.patch", "extra.patch"]),
    ]
    assert list(parser) == expected


def test_parse_append_array_to_string() -> None:
    """
    must preserve a string as the first element when appending an array
    """
    parser = PkgbuildParser(BytesIO(b"source=base.patch\nsource+=(extra.patch)"))
    assert list(parser) == [
        PkgbuildPatch("source", "base.patch"),
        PkgbuildPatch("source", ["base.patch", "extra.patch"]),
    ]


def test_parse_array() -> None:
    """
    must parse array
    """
    parser = PkgbuildParser(BytesIO(b"var=(first second)"))
    assert list(parser.parse()) == [PkgbuildPatch("var", ["first", "second"])]


def test_parse_array_escaped() -> None:
    """
    must correctly process quoted brackets
    """
    parser = PkgbuildParser(BytesIO(b"""var=(first "(" second)"""))
    assert list(parser.parse()) == [PkgbuildPatch("var", ["first", "(", "second"])]

    parser = PkgbuildParser(BytesIO(b"""var=(first ")" second)"""))
    assert list(parser.parse()) == [PkgbuildPatch("var", ["first", ")", "second"])]

    parser = PkgbuildParser(BytesIO(b"""var=(first ')' second)"""))
    assert list(parser.parse()) == [PkgbuildPatch("var", ["first", ")", "second"])]

    parser = PkgbuildParser(BytesIO(b"""var=(first \\) second)"""))
    assert list(parser.parse()) == [PkgbuildPatch("var", ["first", ")", "second"])]


def test_parse_array_comment() -> None:
    """
    must parse array with comments inside
    """
    parser = PkgbuildParser(BytesIO(b"""validpgpkeys=(
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


def test_parse_array_exception() -> None:
    """
    must raise exception if there is no closing bracket
    """
    parser = PkgbuildParser(BytesIO(b"var=(first second"))
    with pytest.raises(PkgbuildParserError):
        list(parser.parse())


def test_parse_function() -> None:
    """
    must parse function
    """
    parser = PkgbuildParser(BytesIO(b"var() { echo hello world; } "))
    assert list(parser.parse()) == [PkgbuildPatch("var()", "{ echo hello world; }")]


def test_parse_function_eof() -> None:
    """
    must parse function with "}" at the end of the file
    """
    parser = PkgbuildParser(BytesIO(b"var() { echo hello world; }"))
    assert list(parser.parse()) == [PkgbuildPatch("var()", "{ echo hello world; }")]


def test_parse_function_escaped() -> None:
    """
    must parse function with bracket in quotes
    """
    parser = PkgbuildParser(BytesIO(b"""var() { echo "hello world {"; } """))
    assert list(parser.parse()) == [PkgbuildPatch("var()", """{ echo "hello world {"; }""")]

    parser = PkgbuildParser(BytesIO(b"""var() { echo hello world "{"; } """))
    assert list(parser.parse()) == [PkgbuildPatch("var()", """{ echo hello world "{"; }""")]

    parser = PkgbuildParser(BytesIO(b"""var() { echo "hello world }"; } """))
    assert list(parser.parse()) == [PkgbuildPatch("var()", """{ echo "hello world }"; }""")]

    parser = PkgbuildParser(BytesIO(b"""var() { echo hello world "}"; } """))
    assert list(parser.parse()) == [PkgbuildPatch("var()", """{ echo hello world "}"; }""")]

    parser = PkgbuildParser(BytesIO(b"""var() { echo hello world '}'; } """))
    assert list(parser.parse()) == [PkgbuildPatch("var()", """{ echo hello world '}'; }""")]

    parser = PkgbuildParser(BytesIO(b"""var() { echo hello world \\}; } """))
    assert list(parser.parse()) == [PkgbuildPatch("var()", """{ echo hello world \\}; }""")]


def test_parse_function_exception() -> None:
    """
    must raise exception if no bracket found
    """
    parser = PkgbuildParser(BytesIO(b"var() echo hello world } "))
    with pytest.raises(PkgbuildParserError):
        list(parser.parse())

    parser = PkgbuildParser(BytesIO(b"var() { echo hello world"))
    with pytest.raises(PkgbuildParserError):
        list(parser.parse())


def test_parse_function_inner_shell() -> None:
    """
    must parse function with inner shell
    """
    parser = PkgbuildParser(BytesIO(b"var() { { echo hello world; }; } "))
    assert list(parser.parse()) == [PkgbuildPatch("var()", "{ { echo hello world; }; }")]


def test_parse_function_spaces() -> None:
    """
    must parse function with spaces before body
    """
    parser = PkgbuildParser(BytesIO(b"var()   { echo hello world; } "))
    assert list(parser.parse()) == [PkgbuildPatch("var()", "{ echo hello world; }")]


def test_parse_token_comment() -> None:
    """
    must correctly parse comment
    """
    parser = PkgbuildParser(BytesIO(b"""first=1 # comment
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
    with pkgbuild.open("rb") as content:
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
            PkgbuildPatch("func()", """{ single line; }"""),
            PkgbuildPatch("func()", """{
    multi
    line
}"""),
            PkgbuildPatch("func()", """{
    c
    multi
    line
}"""),
            PkgbuildPatch("func()", """{
    # comment
    multi
    line
}"""),
            PkgbuildPatch("func()", """{
    body
}"""),
            PkgbuildPatch("func()", """{
    body
}"""),
            PkgbuildPatch("function_with-package-name()", """{ body; }"""),
            PkgbuildPatch("func()", """{
    first
    { inner shell; }
    last
}"""),
            PkgbuildPatch("func()", """{
    body "{" argument
}"""),
            PkgbuildPatch("func()", """{
    body "}" argument
}"""),
            PkgbuildPatch("func()", """{
    body '{' argument
}"""),
            PkgbuildPatch("func()", """{
    body '}' argument
}"""),
            PkgbuildPatch("func()", """{
    # we don't care about unclosed quotation in comments
    body # no, I said we really don't care
}"""),
            PkgbuildPatch("func()", """{
  mv "$pkgdir"/usr/share/fonts/站酷小薇体 "$pkgdir"/usr/share/fonts/zcool-xiaowei-regular
  mv "$pkgdir"/usr/share/licenses/"$pkgname"/LICENSE.站酷小薇体 "$pkgdir"/usr/share/licenses/"$pkgname"/LICENSE.zcool-xiaowei-regular
}"""),
            PkgbuildPatch("var", "value"),
            PkgbuildPatch("array", ["first", "second", "third"]),
            PkgbuildPatch("pkgver()", """{
  cd aften
  _ver="$(cat CMakeLists.txt | grep -e SO_MAJOR_VERSION -e SO_MINOR_VERSION -e SO_BUILD_VERSION | cut -d '"' -f2 | head -n3)"
  echo "$(echo ${_ver} | tr ' ' .).r$(git rev-list --count HEAD).$(git rev-parse --short HEAD)"
}"""),
        ]
