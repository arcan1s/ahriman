from io import BytesIO
from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import MagicMock, PropertyMock

from ahriman.core.exceptions import UnknownPackageError
from ahriman.models.filesystem_package import FilesystemPackage
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


def test_load_pacman_package(package_archive_ahriman: PackageArchive, mocker: MockerFixture) -> None:
    """
    must correctly load filesystem package from pacman
    """
    directory = f"{package_archive_ahriman.package.base}-{package_archive_ahriman.package.version}"
    path = Path("/") / "var" / "lib" / "pacman" / "local" / directory / "files"
    package = MagicMock()
    type(package).depends = PropertyMock(return_value=["depends"])
    type(package).opt_depends = PropertyMock(return_value=["opt_depends"])
    info_mock = mocker.patch("ahriman.core.alpm.remote.OfficialSyncdb.info", return_value=package)

    assert package_archive_ahriman._load_pacman_package(path) == FilesystemPackage(
        package_name=package_archive_ahriman.package.base,
        depends={"depends"},
        opt_depends={"opt_depends"},
    )
    info_mock.assert_called_once_with(package_archive_ahriman.package.base, pacman=package_archive_ahriman.pacman)


def test_load_pacman_package_exception(package_archive_ahriman: PackageArchive, mocker: MockerFixture) -> None:
    """
    must return empty package if no package found
    """
    directory = f"{package_archive_ahriman.package.base}-{package_archive_ahriman.package.version}"
    path = Path("/") / "var" / "lib" / "pacman" / "local" / directory / "files"
    mocker.patch("ahriman.core.alpm.remote.OfficialSyncdb.info",
                 side_effect=UnknownPackageError(package_archive_ahriman.package.base))

    assert package_archive_ahriman._load_pacman_package(path) == FilesystemPackage(
        package_name=package_archive_ahriman.package.base,
        depends=set(),
        opt_depends=set(),
    )


def test_raw_dependencies_packages(package_archive_ahriman: PackageArchive, mocker: MockerFixture) -> None:
    """
    must correctly extract raw dependencies list
    """
    packages = {
        package_archive_ahriman.package.base: FilesystemPackage(
            package_name=package_archive_ahriman.package.base,
            depends=set(),
            opt_depends=set(),
            directories=[Path("usr") / "dir2"],
            files=[Path("file1")],
        ),
        "package1": FilesystemPackage(
            package_name="package1",
            depends=set(),
            opt_depends=set(),
            directories=[Path("package1") / "dir1", Path("usr") / "dir2"],
            files=[Path("package1") / "file1", Path("package1") / "file2"],
        ),
        "package2": FilesystemPackage(
            package_name="package2",
            depends=set(),
            opt_depends=set(),
            directories=[Path("usr") / "dir2", Path("package2") / "dir3", Path("package2") / "dir4"],
            files=[Path("package2") / "file4", Path("package2") / "file3"],
        ),
    }
    mocker.patch("ahriman.models.package_archive.PackageArchive.installed_packages", return_value=packages)
    mocker.patch("ahriman.models.package_archive.PackageArchive.depends_on_paths", return_value=(
        {"file1", "file3"},
        {Path("usr") / "dir2", Path("dir3"), Path("package2") / "dir4"},
    ))

    result = package_archive_ahriman._raw_dependencies_packages()
    assert result == {
        Path("package1") / "file1": [packages["package1"]],
        Path("package2") / "file3": [packages["package2"]],
        Path("package2") / "dir4": [packages["package2"]],
        Path("usr") / "dir2": [packages["package1"], packages["package2"]],
    }


def test_refine_dependencies(package_archive_ahriman: PackageArchive, mocker: MockerFixture) -> None:
    """
    must correctly refine dependencies list
    """
    base_package = MagicMock()
    type(base_package).depends = PropertyMock(return_value=["base"])
    info_mock = mocker.patch("ahriman.core.alpm.remote.OfficialSyncdb.info", return_value=base_package)

    path1 = Path("usr") / "lib" / "python3.12"
    path2 = path1 / "site-packages"
    path3 = Path("usr") / "lib" / "path"
    path4 = Path("usr") / "lib" / "whatever"
    path5 = Path("usr") / "share" / "applications"
    path6 = Path("etc")

    package1 = FilesystemPackage(package_name="package1", depends={"package5"}, opt_depends={"package2"})
    package2 = FilesystemPackage(package_name="package2", depends={"package1"}, opt_depends=set())
    package3 = FilesystemPackage(package_name="package3", depends=set(), opt_depends={"package1"})
    package4 = FilesystemPackage(package_name="base", depends=set(), opt_depends=set())
    package5 = FilesystemPackage(package_name="package5", depends={"package1"}, opt_depends=set())
    package6 = FilesystemPackage(package_name="package6", depends=set(), opt_depends=set())

    assert package_archive_ahriman._refine_dependencies({
        path1: [package1, package2, package3, package5, package6],
        path2: [package1, package2, package3, package5],
        path3: [package1, package4],
        path4: [package1],
        path5: [package1],
        path6: [package1],
    }) == {
        path1: [package6],
        path2: [package1, package5],
        path4: [package1],
    }
    info_mock.assert_called_once_with("base", pacman=package_archive_ahriman.pacman)


def test_depends_on(package_archive_ahriman: PackageArchive, mocker: MockerFixture) -> None:
    """
    must extract packages and files which are dependencies for the package
    """
    raw_mock = mocker.patch("ahriman.models.package_archive.PackageArchive._raw_dependencies_packages",
                            return_value="1")
    refined_mock = mocker.patch("ahriman.models.package_archive.PackageArchive._refine_dependencies", return_value={
        Path("package1") / "file1": [FilesystemPackage(package_name="package1", depends=set(), opt_depends=set())],
        Path("package2") / "file3": [FilesystemPackage(package_name="package2", depends=set(), opt_depends=set())],
        Path("package2") / "dir4": [FilesystemPackage(package_name="package2", depends=set(), opt_depends=set())],
        Path("usr") / "dir2": [
            FilesystemPackage(package_name="package1", depends=set(), opt_depends=set()),
            FilesystemPackage(package_name="package2", depends=set(), opt_depends=set()),
        ],
    })

    result = package_archive_ahriman.depends_on()
    raw_mock.assert_called_once_with()
    refined_mock.assert_called_once_with("1")
    assert result.paths == {
        "package1/file1": ["package1"],
        "package2/file3": ["package2"],
        "package2/dir4": ["package2"],
        "usr/dir2": ["package1", "package2"]
    }


def test_depends_on_paths(package_archive_ahriman: PackageArchive, mocker: MockerFixture) -> None:
    """
    must correctly extract dependencies
    """
    package_dir = package_archive_ahriman.root / "build" / \
        package_archive_ahriman.package.base / "pkg" / package_archive_ahriman.package.base
    dynamic_mock = mocker.patch("ahriman.models.package_archive.PackageArchive.dynamic_needed", return_value=["lib"])
    walk_mock = mocker.patch("ahriman.models.package_archive.walk", return_value=[
        package_dir / "root" / "file",
        Path("directory"),
    ])
    mocker.patch("pathlib.Path.is_file", autospec=True, side_effect=lambda path: path != Path("directory"))

    dependencies, roots = package_archive_ahriman.depends_on_paths()
    assert dependencies == {"lib"}
    assert roots == {Path("root")}
    dynamic_mock.assert_called_once_with(package_dir / "root" / "file")
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
    assert Path("usr") in result[package_archive_ahriman.package.base].directories
    assert Path("usr/bin/ahriman") in result[package_archive_ahriman.package.base].files
    walk_mock.assert_called_once_with(package_archive_ahriman.root / "var" / "lib" / "pacman" / "local")
    read_mock.assert_called_once_with(encoding="utf8")
