import pytest

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.build_tools.task import Task
from ahriman.models.pkgbuild_patch import PkgbuildPatch


def test_package_archives(task_ahriman: Task, mocker: MockerFixture) -> None:
    """
    must correctly return list of new files
    """
    mocker.patch("pathlib.Path.iterdir", return_value=[
        Path(f"{task_ahriman.package.base}-{task_ahriman.package.version}-any.pkg.tar.xz"),
        Path(f"{task_ahriman.package.base}-debug-{task_ahriman.package.version}-any.pkg.tar.xz"),
        Path("source.pkg.tar.xz"),
        Path("randomfile"),
        Path("namcap.log"),
    ])
    assert task_ahriman._package_archives(Path("local"), [Path("source.pkg.tar.xz")]) == [
        Path(f"{task_ahriman.package.base}-{task_ahriman.package.version}-any.pkg.tar.xz"),
        Path(f"{task_ahriman.package.base}-debug-{task_ahriman.package.version}-any.pkg.tar.xz"),
    ]


def test_package_archives_no_debug(task_ahriman: Task, mocker: MockerFixture) -> None:
    """
    must correctly return list of new files without debug packages
    """
    task_ahriman.include_debug_packages = False
    mocker.patch("pathlib.Path.iterdir", return_value=[
        Path(f"{task_ahriman.package.base}-{task_ahriman.package.version}-any.pkg.tar.xz"),
        Path(f"{task_ahriman.package.base}-debug-{task_ahriman.package.version}-any.pkg.tar.xz"),
        Path("source.pkg.tar.xz"),
        Path("randomfile"),
        Path("namcap.log"),
    ])
    assert task_ahriman._package_archives(Path("local"), [Path("source.pkg.tar.xz")]) == [
        Path(f"{task_ahriman.package.base}-{task_ahriman.package.version}-any.pkg.tar.xz"),
    ]


def test_build(task_ahriman: Task, mocker: MockerFixture) -> None:
    """
    must build package
    """
    local = Path("local")
    mocker.patch("pathlib.Path.iterdir", return_value=["file"])
    check_output_mock = mocker.patch("ahriman.core.build_tools.task.check_output")
    archives_mock = mocker.patch("ahriman.core.build_tools.task.Task._package_archives",
                                 return_value=[task_ahriman.package.base])

    assert task_ahriman.build(local) == [task_ahriman.package.base]
    check_output_mock.assert_called_once_with(
        "extra-x86_64-build", "-r", str(task_ahriman.paths.chroot), "--", "--", "--skippgpcheck",
        exception=pytest.helpers.anyvar(int),
        cwd=local,
        logger=task_ahriman.logger,
        user=task_ahriman.uid,
        environment={},
    )
    archives_mock.assert_called_once_with(local, ["file"])


def test_build_environment(task_ahriman: Task, mocker: MockerFixture) -> None:
    """
    must build package with environment variables set
    """
    local = Path("local")
    mocker.patch("pathlib.Path.iterdir", return_value=["file"])
    mocker.patch("ahriman.core.build_tools.task.Task._package_archives", return_value=[task_ahriman.package.base])
    check_output_mock = mocker.patch("ahriman.core.build_tools.task.check_output")

    environment = {"variable": "value"}

    task_ahriman.build(local, **environment, empty=None)
    check_output_mock.assert_called_once_with(
        "extra-x86_64-build", "-r", str(task_ahriman.paths.chroot), "--", "--", "--skippgpcheck",
        exception=pytest.helpers.anyvar(int),
        cwd=local,
        logger=task_ahriman.logger,
        user=task_ahriman.uid,
        environment=environment,
    )


def test_build_dry_run(task_ahriman: Task, mocker: MockerFixture) -> None:
    """
    must run devtools in dry-run mode
    """
    local = Path("local")
    mocker.patch("pathlib.Path.iterdir", return_value=["file"])
    mocker.patch("ahriman.core.build_tools.task.Task._package_archives", return_value=[task_ahriman.package.base])
    check_output_mock = mocker.patch("ahriman.core.build_tools.task.check_output")

    assert task_ahriman.build(local, dry_run=True) == [task_ahriman.package.base]
    check_output_mock.assert_called_once_with(
        "extra-x86_64-build", "-r", str(task_ahriman.paths.chroot), "--", "--", "--skippgpcheck", "--nobuild",
        exception=pytest.helpers.anyvar(int),
        cwd=local,
        logger=task_ahriman.logger,
        user=task_ahriman.uid,
        environment={},
    )


def test_init(task_ahriman: Task, mocker: MockerFixture) -> None:
    """
    must copy tree instead of fetch
    """
    patches = [PkgbuildPatch("hash", "patch")]
    mocker.patch("ahriman.models.package.Package.from_build", return_value=task_ahriman.package)
    load_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.load", return_value="sha")

    assert task_ahriman.init(Path("ahriman"), patches, None) == "sha"
    load_mock.assert_called_once_with(Path("ahriman"), task_ahriman.package, patches, task_ahriman.paths)


def test_init_vcs(task_ahriman: Task, mocker: MockerFixture) -> None:
    """
    must copy tree instead of fetch
    """
    task_ahriman.package.base += "-git"
    mocker.patch("ahriman.models.package.Package.from_build", return_value=task_ahriman.package)
    load_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.load", return_value="sha")
    build_mock = mocker.patch("ahriman.core.build_tools.task.Task.build")

    local = Path("ahriman")
    assert task_ahriman.init(local, [], None) == "sha"
    load_mock.assert_called_once_with(local, task_ahriman.package, [], task_ahriman.paths)
    build_mock.assert_called_once_with(local, dry_run=True)


def test_init_bump_pkgrel(task_ahriman: Task, mocker: MockerFixture) -> None:
    """
    must bump pkgrel if it is same as provided
    """
    mocker.patch("ahriman.models.package.Package.from_build", return_value=task_ahriman.package)
    mocker.patch("ahriman.core.build_tools.sources.Sources.load", return_value="sha")
    write_mock = mocker.patch("ahriman.models.pkgbuild_patch.PkgbuildPatch.write")

    local = Path("ahriman")
    assert task_ahriman.init(local, [], task_ahriman.package.version) == "sha"
    write_mock.assert_called_once_with(local / "PKGBUILD")


def test_init_bump_pkgrel_skip(task_ahriman: Task, mocker: MockerFixture) -> None:
    """
    must keep pkgrel if version is different from provided
    """
    task_ahriman.package.version = "2.0.0-1"
    mocker.patch("ahriman.models.package.Package.from_build", return_value=task_ahriman.package)
    mocker.patch("ahriman.core.build_tools.sources.Sources.load", return_value="sha")
    write_mock = mocker.patch("ahriman.models.pkgbuild_patch.PkgbuildPatch.write")

    assert task_ahriman.init(Path("ahriman"), [], "1.0.0-1") == "sha"
    write_mock.assert_not_called()
