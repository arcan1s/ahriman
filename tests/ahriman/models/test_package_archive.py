from io import BytesIO
from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.models.package_archive import PackageArchive


def test_dynamic_needed(mocker: MockerFixture) -> None:
    """
    must correctly define list of dynamically linked libraries
    """
    mocker.patch("ahriman.models.package_archive.PackageArchive.is_elf", return_value=True)

    linked = PackageArchive.dynamic_needed(Path(".tox") / "tests" / "bin" / "python")
    assert linked
    assert next(library for library in linked if library.startswith("libpython"))
    assert next(library for library in linked if library.startswith("libc"))


def test_dynamic_needed_not_elf(mocker: MockerFixture) -> None:
    """
    must skip checking if not an elf file
    """
    mocker.patch("ahriman.models.package_archive.PackageArchive.is_elf", return_value=False)
    assert not PackageArchive.dynamic_needed(Path(".tox") / "tests" / "bin" / "python")


def test_dynamic_needed_no_section(mocker: MockerFixture) -> None:
    """
    must skip checking if there was no dynamic section found
    """
    mocker.patch("ahriman.models.package_archive.PackageArchive.is_elf", return_value=True)
    mocker.patch("elftools.elf.elffile.ELFFile.iter_sections", return_value=[])
    assert not PackageArchive.dynamic_needed(Path(".tox") / "tests" / "bin" / "python")


def test_is_elf() -> None:
    """
    must correctly define elf file
    """
    assert not PackageArchive.is_elf(BytesIO())
    assert not PackageArchive.is_elf(BytesIO(b"random string"))
    assert PackageArchive.is_elf(BytesIO(b"\x7fELF"))
    assert PackageArchive.is_elf(BytesIO(b"\x7fELF\nrandom string"))


def test_depends_on(package_archive_ahriman: PackageArchive, mocker: MockerFixture) -> None:
    """
    must extract packages and files which are dependencies for the package
    """
    mocker.patch("ahriman.models.package_archive.PackageArchive.installed_packages", return_value={
        package_archive_ahriman.package.base: ([Path("usr") / "dir2"], [Path("file1")]),
        "package1": (
            [Path("package1") / "dir1", Path("usr") / "dir2"],
            [Path("package1") / "file1", Path("package1") / "file2"],
        ),
        "package2": (
            [Path("usr") / "dir2", Path("package2") / "dir3", Path("package2") / "dir4"],
            [Path("package2") / "file4", Path("package2") / "file3"],
        ),
    })
    mocker.patch("ahriman.models.package_archive.PackageArchive.depends_on_paths", return_value=(
        {"file1", "file3"},
        {Path("usr") / "dir2", Path("dir3"), Path("package2") / "dir4"},
    ))

    result = package_archive_ahriman.depends_on()
    assert result.package_base == package_archive_ahriman.package.base
    assert result.paths == {
        Path("package1") / "file1": ["package1"],
        Path("package2") / "file3": ["package2"],
        Path("package2") / "dir4": ["package2"],
        Path("package2") / "file3": ["package2"],
        Path("usr") / "dir2": ["package1", "package2"]
    }


def test_depends_on_paths(package_archive_ahriman: PackageArchive, mocker: MockerFixture) -> None:
    """
    must correctly extract dependencies
    """
    package_dir = package_archive_ahriman.root / "build" / package_archive_ahriman.package.base / "pkg"
    dynamic_mock = mocker.patch("ahriman.models.package_archive.PackageArchive.dynamic_needed", return_value=["lib"])
    walk_mock = mocker.patch("ahriman.models.package_archive.walk", return_value=[
        package_dir / package_archive_ahriman.package.base / "root" / "file",
        Path("directory"),
    ])
    mocker.patch("pathlib.Path.is_file", autospec=True, side_effect=lambda path: path != Path("directory"))

    dependencies, roots = package_archive_ahriman.depends_on_paths()
    assert dependencies == {"lib"}
    assert roots == {Path("root")}
    dynamic_mock.assert_called_once_with(package_dir / package_archive_ahriman.package.base / "root" / "file")
    walk_mock.assert_called_once_with(package_dir)


def test_installed_packages(package_archive_ahriman: PackageArchive, mocker: MockerFixture,
                            resource_path_root: Path) -> None:
    """
    must load list of installed packages and their files
    """
    walk_mock = mocker.patch("ahriman.models.package_archive.walk", return_value=[
        Path("ahriman-2.13.3-1") / "desc",
        Path("ahriman-2.13.3-1") / "files",
    ])
    files = (resource_path_root / "models" / "package_ahriman_files").read_text(encoding="utf8")
    read_mock = mocker.patch("pathlib.Path.read_text", return_value=files)

    result = package_archive_ahriman.installed_packages()
    assert result
    assert Path("usr") in result[package_archive_ahriman.package.base][0]
    assert Path("usr/bin/ahriman") in result[package_archive_ahriman.package.base][1]
    walk_mock.assert_called_once_with(package_archive_ahriman.root / "var" / "lib" / "pacman" / "local")
    read_mock.assert_called_once_with(encoding="utf8")
