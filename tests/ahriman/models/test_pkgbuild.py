import pytest

from io import StringIO
from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.models.pkgbuild import Pkgbuild
from ahriman.models.pkgbuild_patch import PkgbuildPatch


def test_variables(pkgbuild_ahriman: Pkgbuild) -> None:
    """
    must correctly generate list of variables
    """
    assert pkgbuild_ahriman.variables
    assert "pkgver" in pkgbuild_ahriman.variables
    assert "build" not in pkgbuild_ahriman.variables
    assert "source" not in pkgbuild_ahriman.variables


def test_from_file(pkgbuild_ahriman: Pkgbuild, mocker: MockerFixture) -> None:
    """
    must correctly load from file
    """
    open_mock = mocker.patch("pathlib.Path.open")
    load_mock = mocker.patch("ahriman.models.pkgbuild.Pkgbuild.from_io", return_value=pkgbuild_ahriman)

    assert Pkgbuild.from_file(Path("local"))
    open_mock.assert_called_once_with()
    load_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_from_io(pkgbuild_ahriman: Pkgbuild, mocker: MockerFixture) -> None:
    """
    must correctly load from io
    """
    load_mock = mocker.patch("ahriman.core.alpm.pkgbuild_parser.PkgbuildParser.parse",
                             return_value=pkgbuild_ahriman.fields.values())
    assert Pkgbuild.from_io(StringIO("mock")) == pkgbuild_ahriman
    load_mock.assert_called_once_with()


def test_from_io_pkgbase(pkgbuild_ahriman: Pkgbuild, mocker: MockerFixture) -> None:
    """
    must assign missing pkgbase if pkgname is presented
    """
    mocker.patch("ahriman.core.alpm.pkgbuild_parser.PkgbuildParser.parse", side_effect=[
        [value for key, value in pkgbuild_ahriman.fields.items() if key not in ("pkgbase",)],
        [value for key, value in pkgbuild_ahriman.fields.items() if key not in ("pkgbase", "pkgname",)],
        [value for key, value in pkgbuild_ahriman.fields.items()] + [PkgbuildPatch("pkgbase", "pkgbase")],
    ])

    assert Pkgbuild.from_io(StringIO("mock"))["pkgbase"] == pkgbuild_ahriman["pkgname"]
    assert "pkgbase" not in Pkgbuild.from_io(StringIO("mock"))
    assert Pkgbuild.from_io(StringIO("mock"))["pkgbase"] == "pkgbase"


def test_from_io_empty(pkgbuild_ahriman: Pkgbuild, mocker: MockerFixture) -> None:
    """
    must skip empty patches
    """
    mocker.patch("ahriman.core.alpm.pkgbuild_parser.PkgbuildParser.parse",
                 return_value=list(pkgbuild_ahriman.fields.values()) + [PkgbuildPatch("", "")])
    assert Pkgbuild.from_io(StringIO("mock")) == pkgbuild_ahriman


def test_packages(pkgbuild_ahriman: Pkgbuild) -> None:
    """
    must correctly generate load package function
    """
    assert pkgbuild_ahriman.packages() == {pkgbuild_ahriman["pkgbase"]: Pkgbuild({})}


def test_packages_multi(resource_path_root: Path) -> None:
    """
    must correctly generate load list of package functions
    """
    pkgbuild = Pkgbuild.from_file(resource_path_root / "models" / "package_gcc10_pkgbuild")
    packages = pkgbuild.packages()

    assert all(pkgname in packages for pkgname in pkgbuild["pkgname"])
    assert all("pkgdesc" in package for package in packages.values())
    assert all("depends" in package for package in packages.values())


def test_getitem(pkgbuild_ahriman: Pkgbuild) -> None:
    """
    must return element by key
    """
    assert pkgbuild_ahriman["pkgname"] == pkgbuild_ahriman.fields["pkgname"].value
    assert pkgbuild_ahriman["build()"] == pkgbuild_ahriman.fields["build()"].substitute(pkgbuild_ahriman.variables)


def test_getitem_substitute(pkgbuild_ahriman: Pkgbuild) -> None:
    """
    must return element by key and substitute variables
    """
    pkgbuild_ahriman.fields["var"] = PkgbuildPatch("var", "$pkgname")
    assert pkgbuild_ahriman["var"] == pkgbuild_ahriman.fields["pkgname"].value


def test_getitem_function(pkgbuild_ahriman: Pkgbuild) -> None:
    """
    must return element by key with fallback to function
    """
    assert pkgbuild_ahriman["build"] == pkgbuild_ahriman.fields["build()"].substitute(pkgbuild_ahriman.variables)

    pkgbuild_ahriman.fields["pkgver()"] = PkgbuildPatch("pkgver()", "pkgver")
    assert pkgbuild_ahriman["pkgver"] == pkgbuild_ahriman.fields["pkgver"].value
    assert pkgbuild_ahriman["pkgver()"] == pkgbuild_ahriman.fields["pkgver()"].value


def test_getitem_exception(pkgbuild_ahriman: Pkgbuild) -> None:
    """
    must raise KeyError for unknown key
    """
    with pytest.raises(KeyError):
        assert pkgbuild_ahriman["field"]


def test_iter(pkgbuild_ahriman: Pkgbuild) -> None:
    """
    must return keys iterator
    """
    for key in list(pkgbuild_ahriman):
        del pkgbuild_ahriman.fields[key]
    assert not pkgbuild_ahriman.fields


def test_len(pkgbuild_ahriman: Pkgbuild) -> None:
    """
    must return length of the map
    """
    assert len(pkgbuild_ahriman) == len(pkgbuild_ahriman.fields)
