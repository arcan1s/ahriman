import copy

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import MagicMock, call as MockCall

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.configuration import Configuration
from ahriman.core.utils import utcnow
from ahriman.models.aur_package import AURPackage
from ahriman.models.package import Package
from ahriman.models.package_description import PackageDescription
from ahriman.models.pkgbuild import Pkgbuild
from ahriman.models.pkgbuild_patch import PkgbuildPatch


def test_depends(package_python_schedule: Package) -> None:
    """
    must return combined list of dependencies
    """
    assert all(
        set(package_python_schedule.depends).intersection(package.depends)
        for package in package_python_schedule.packages.values()
    )


def test_depends_build(package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must return full list of packages required for build
    """
    assert all(
        set(package_ahriman.depends_build).intersection(package.depends)
        for package in package_ahriman.packages.values()
    )
    assert all(
        set(package_ahriman.depends_build).intersection(package.make_depends)
        for package in package_ahriman.packages.values()
    )
    assert all(
        set(package_ahriman.depends_build).intersection(package.check_depends)
        for package in package_ahriman.packages.values()
    )

    assert all(
        set(package_python_schedule.depends_build).intersection(package.depends)
        for package in package_python_schedule.packages.values()
    )
    # there is no make dependencies for python-schedule


def test_depends_build_with_version_and_overlap(mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must load correct list of dependencies with version
    """
    pkgbuild = resource_path_root / "models" / "package_gcc10_pkgbuild"
    mocker.patch("ahriman.models.pkgbuild.Pkgbuild.from_file", return_value=Pkgbuild.from_file(pkgbuild))

    package_gcc10 = Package.from_build(Path("local"), "x86_64", None)
    assert package_gcc10.depends_build == {
        "glibc", "zstd",  # depends
        "doxygen", "binutils", "git", "libmpc", "python",  # make depends
        "dejagnu", "inetutils",  # check depends
    }


def test_depends_check(package_ahriman: Package) -> None:
    """
    must return list of test dependencies
    """
    assert all(
        set(package_ahriman.depends_check).intersection(package.check_depends)
        for package in package_ahriman.packages.values()
    )


def test_depends_make(package_ahriman: Package) -> None:
    """
    must return list of make dependencies
    """
    assert all(
        set(package_ahriman.depends_make).intersection(package.make_depends)
        for package in package_ahriman.packages.values()
    )


def test_depends_opt(package_ahriman: Package) -> None:
    """
    must return list of optional dependencies
    """
    assert all(
        set(package_ahriman.depends_opt).intersection(package.opt_depends)
        for package in package_ahriman.packages.values()
    )


def test_groups(package_ahriman: Package) -> None:
    """
    must return list of groups for each package
    """
    assert all(
        all(group in package_ahriman.groups for group in package.groups)
        for package in package_ahriman.packages.values()
    )
    assert sorted(package_ahriman.groups) == package_ahriman.groups


def test_is_single_package_false(package_python_schedule: Package) -> None:
    """
    python-schedule must not be single package
    """
    assert not package_python_schedule.is_single_package


def test_is_single_package_true(package_ahriman: Package) -> None:
    """
    ahriman must be single package
    """
    assert package_ahriman.is_single_package


def test_is_vcs_false(package_ahriman: Package) -> None:
    """
    ahriman must not be VCS package
    """
    assert not package_ahriman.is_vcs


def test_is_vcs_true(package_tpacpi_bat_git: Package) -> None:
    """
    tpacpi-bat-git must be VCS package
    """
    assert package_tpacpi_bat_git.is_vcs


def test_licenses(package_ahriman: Package) -> None:
    """
    must return list of licenses for each package
    """
    assert all(
        all(lic in package_ahriman.licenses for lic in package.licenses)
        for package in package_ahriman.packages.values()
    )
    assert sorted(package_ahriman.licenses) == package_ahriman.licenses


def test_packages_full(package_ahriman: Package) -> None:
    """
    must return full list of packages including provides
    """
    package_ahriman.packages[package_ahriman.base].provides = [f"{package_ahriman.base}-git"]
    assert package_ahriman.packages_full == [package_ahriman.base, f"{package_ahriman.base}-git"]


def test_from_archive(package_ahriman: Package, pyalpm_handle: MagicMock, mocker: MockerFixture) -> None:
    """
    must construct package from alpm library
    """
    mocker.patch("ahriman.models.package_description.PackageDescription.from_package",
                 return_value=package_ahriman.packages[package_ahriman.base])
    generated = Package.from_archive(Path("path"), pyalpm_handle)
    generated.remote = package_ahriman.remote

    assert generated == package_ahriman


def test_from_aur(package_ahriman: Package, aur_package_ahriman: AURPackage, mocker: MockerFixture) -> None:
    """
    must construct package from aur
    """
    info_mock = mocker.patch("ahriman.core.alpm.remote.AUR.info", return_value=aur_package_ahriman)

    package = Package.from_aur(package_ahriman.base, package_ahriman.packager)
    info_mock.assert_called_once_with(package_ahriman.base, include_provides=False)
    assert package_ahriman.base == package.base
    assert package_ahriman.version == package.version
    assert package_ahriman.packages.keys() == package.packages.keys()
    assert package_ahriman.packager == package.packager


def test_from_aur_include_provides(package_ahriman: Package, aur_package_ahriman: AURPackage,
                                   mocker: MockerFixture) -> None:
    """
    must construct package from aur by using provides list
    """
    info_mock = mocker.patch("ahriman.core.alpm.remote.AUR.info", return_value=aur_package_ahriman)
    Package.from_aur(package_ahriman.base, package_ahriman.packager, include_provides=True)
    info_mock.assert_called_once_with(package_ahriman.base, include_provides=True)


def test_from_build(package_ahriman: Package, mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must construct package from PKGBUILD
    """
    pkgbuild = resource_path_root / "models" / "package_ahriman_pkgbuild"
    mocker.patch("ahriman.models.pkgbuild.Pkgbuild.from_file", return_value=Pkgbuild.from_file(pkgbuild))

    package = Package.from_build(Path("path"), "x86_64", "packager")
    assert package_ahriman.packages.keys() == package.packages.keys()
    package_ahriman.packages = package.packages  # we are not going to test PackageDescription here
    package_ahriman.remote = package.remote
    assert package_ahriman == package


def test_from_build_multiple_packages(mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must construct package from PKGBUILD with dependencies per-package overrides
    """
    pkgbuild = resource_path_root / "models" / "package_gcc10_pkgbuild"
    mocker.patch("ahriman.models.pkgbuild.Pkgbuild.from_file", return_value=Pkgbuild.from_file(pkgbuild))

    package = Package.from_build(Path("path"), "x86_64", None)
    assert package.packages == {
        "gcc10": PackageDescription(
            depends=["gcc10-libs=10.5.0-2", "binutils>=2.28", "libmpc", "zstd"],
            make_depends=["binutils", "doxygen", "git", "libmpc", "python"],
            opt_depends=[],
            check_depends=["dejagnu", "inetutils"],
        ),
        "gcc10-libs": PackageDescription(
            depends=["glibc>=2.27"],
            make_depends=["binutils", "doxygen", "git", "libmpc", "python"],
            opt_depends=[],
            check_depends=["dejagnu", "inetutils"],
        ),
        "gcc10-fortran": PackageDescription(
            depends=["gcc10=10.5.0-2"],
            make_depends=["binutils", "doxygen", "git", "libmpc", "python"],
            opt_depends=[],
            check_depends=["dejagnu", "inetutils"],
        ),
    }


def test_from_build_architecture(mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must construct package with architecture specific depends list
    """
    pkgbuild = resource_path_root / "models" / "package_jellyfin-ffmpeg6-bin_pkgbuild"
    mocker.patch("ahriman.models.pkgbuild.Pkgbuild.from_file", return_value=Pkgbuild.from_file(pkgbuild))

    package = Package.from_build(Path("path"), "x86_64", None)
    assert package.packages == {
        "jellyfin-ffmpeg6-bin": PackageDescription(
            depends=["glibc"],
            make_depends=[],
            opt_depends=[
                "intel-media-driver: for Intel VAAPI support (Broadwell and newer)",
                "intel-media-sdk: for Intel Quick Sync Video",
                "onevpl-intel-gpu: for Intel Quick Sync Video (12th Gen and newer)",
                "intel-compute-runtime: for Intel OpenCL runtime based Tonemapping",
                "libva-intel-driver: for Intel legacy VAAPI support (10th Gen and older)",
                "libva-mesa-driver: for AMD VAAPI support",
                "nvidia-utils: for Nvidia NVDEC/NVENC support",
                "opencl-amd: for AMD OpenCL runtime based Tonemapping",
                "vulkan-radeon: for AMD RADV Vulkan support",
                "vulkan-intel: for Intel ANV Vulkan support",
            ],
        ),
    }


def test_from_json_view_1(package_ahriman: Package) -> None:
    """
    must construct same object from json
    """
    assert Package.from_json(package_ahriman.view()) == package_ahriman


def test_from_json_view_2(package_python_schedule: Package) -> None:
    """
    must construct same object from json (double package)
    """
    assert Package.from_json(package_python_schedule.view()) == package_python_schedule


def test_from_json_view_3(package_tpacpi_bat_git: Package) -> None:
    """
    must construct same object from json (git package)
    """
    assert Package.from_json(package_tpacpi_bat_git.view()) == package_tpacpi_bat_git


def test_from_official_include_provides(package_ahriman: Package, aur_package_ahriman: AURPackage, pacman: Pacman,
                                        mocker: MockerFixture) -> None:
    """
    must construct package from official repository
    """
    info_mock = mocker.patch("ahriman.core.alpm.remote.Official.info", return_value=aur_package_ahriman)
    Package.from_official(package_ahriman.base, pacman, package_ahriman.packager, include_provides=True)
    info_mock.assert_called_once_with(package_ahriman.base, pacman=pacman, include_provides=True)


def test_from_official(package_ahriman: Package, aur_package_ahriman: AURPackage, pacman: Pacman,
                       mocker: MockerFixture) -> None:
    """
    must construct package from official repository
    """
    info_mock = mocker.patch("ahriman.core.alpm.remote.Official.info", return_value=aur_package_ahriman)

    package = Package.from_official(package_ahriman.base, pacman, package_ahriman.packager)
    info_mock.assert_called_once_with(package_ahriman.base, pacman=pacman, include_provides=False)
    assert package_ahriman.base == package.base
    assert package_ahriman.version == package.version
    assert package_ahriman.packages.keys() == package.packages.keys()
    assert package_ahriman.packager == package.packager


def test_local_files(mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must extract local file sources
    """
    pkgbuild = resource_path_root / "models" / "package_yay_pkgbuild"
    parsed_pkgbuild = Pkgbuild.from_file(pkgbuild)
    parsed_pkgbuild.fields["source"] = PkgbuildPatch("source", ["local-file.tar.gz"])
    mocker.patch("ahriman.models.pkgbuild.Pkgbuild.from_file", return_value=parsed_pkgbuild)
    mocker.patch("ahriman.models.package.Package.supported_architectures", return_value=["any"])

    assert list(Package.local_files(Path("path"))) == [Path("local-file.tar.gz")]


def test_local_files_empty(mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must extract empty local files list when there are no local files
    """
    pkgbuild = resource_path_root / "models" / "package_yay_pkgbuild"
    mocker.patch("ahriman.models.pkgbuild.Pkgbuild.from_file", return_value=Pkgbuild.from_file(pkgbuild))
    mocker.patch("ahriman.models.package.Package.supported_architectures", return_value=["any"])

    assert not list(Package.local_files(Path("path")))


def test_local_files_schema(mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must skip local file source when file schema is used
    """
    pkgbuild = resource_path_root / "models" / "package_yay_pkgbuild"
    parsed_pkgbuild = Pkgbuild.from_file(pkgbuild)
    parsed_pkgbuild.fields["source"] = PkgbuildPatch("source", ["file:///local-file.tar.gz"])
    mocker.patch("ahriman.models.pkgbuild.Pkgbuild.from_file", return_value=parsed_pkgbuild)
    mocker.patch("ahriman.models.package.Package.supported_architectures", return_value=["any"])

    assert not list(Package.local_files(Path("path")))


def test_local_files_with_install(mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must extract local file sources with install file
    """
    pkgbuild = resource_path_root / "models" / "package_yay_pkgbuild"
    parsed_pkgbuild = Pkgbuild.from_file(pkgbuild)
    parsed_pkgbuild.fields["install"] = PkgbuildPatch("install", "install")
    mocker.patch("ahriman.models.pkgbuild.Pkgbuild.from_file", return_value=parsed_pkgbuild)
    mocker.patch("ahriman.models.package.Package.supported_architectures", return_value=["any"])

    assert list(Package.local_files(Path("path"))) == [Path("install")]


def test_supported_architectures(mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must generate list of available architectures
    """
    pkgbuild = resource_path_root / "models" / "package_yay_pkgbuild"
    mocker.patch("ahriman.models.pkgbuild.Pkgbuild.from_file", return_value=Pkgbuild.from_file(pkgbuild))
    assert Package.supported_architectures(Path("path")) == \
        {"i686", "pentium4", "x86_64", "arm", "armv7h", "armv6h", "aarch64", "riscv64"}


def test_actual_version(package_ahriman: Package, configuration: Configuration) -> None:
    """
    must return same actual_version as version is
    """
    assert package_ahriman.actual_version(configuration) == package_ahriman.version


def test_actual_version_vcs(package_tpacpi_bat_git: Package, configuration: Configuration,
                            mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must return valid actual_version for VCS package
    """
    pkgbuild = resource_path_root / "models" / "package_tpacpi-bat-git_pkgbuild"
    mocker.patch("ahriman.models.pkgbuild.Pkgbuild.from_file", return_value=Pkgbuild.from_file(pkgbuild))
    mocker.patch("pathlib.Path.glob", return_value=[Path("local")])
    init_mock = mocker.patch("ahriman.core.build_tools.task.Task.init")
    unlink_mock = mocker.patch("pathlib.Path.unlink")

    assert package_tpacpi_bat_git.actual_version(configuration) == "3.1.r13.g4959b52-1"
    init_mock.assert_called_once_with(configuration.repository_paths.cache_for(package_tpacpi_bat_git.base), [], None)
    unlink_mock.assert_called_once_with()


def test_actual_version_failed(package_tpacpi_bat_git: Package, configuration: Configuration,
                               mocker: MockerFixture) -> None:
    """
    must return same version in case if exception occurred
    """
    mocker.patch("ahriman.core.build_tools.task.Task.init", side_effect=Exception)
    mocker.patch("pathlib.Path.glob", return_value=[Path("local")])
    unlink_mock = mocker.patch("pathlib.Path.unlink")

    assert package_tpacpi_bat_git.actual_version(configuration) == package_tpacpi_bat_git.version
    unlink_mock.assert_called_once_with()


def test_full_depends(package_ahriman: Package, package_python_schedule: Package, pyalpm_package_ahriman: MagicMock,
                      pyalpm_handle: MagicMock) -> None:
    """
    must extract all dependencies from the package
    """
    package_python_schedule.packages[package_python_schedule.base].provides = ["python3-schedule"]

    database_mock = MagicMock()
    database_mock.pkgcache = [pyalpm_package_ahriman]
    pyalpm_handle.handle.get_syncdbs.return_value = [database_mock]

    assert package_ahriman.full_depends(pyalpm_handle, [package_python_schedule]) == package_ahriman.depends

    package_python_schedule.packages[package_python_schedule.base].depends = [package_ahriman.base]
    expected = sorted(set(package_python_schedule.depends + package_ahriman.depends))
    assert package_python_schedule.full_depends(pyalpm_handle, [package_python_schedule]) == expected


def test_is_newer_than(package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must correctly check if package is newer than specified timestamp
    """
    # base checks, true/false
    assert package_ahriman.is_newer_than(package_ahriman.packages[package_ahriman.base].build_date - 1)
    assert not package_ahriman.is_newer_than(package_ahriman.packages[package_ahriman.base].build_date + 1)

    # list check
    min_date = min(package.build_date for package in package_python_schedule.packages.values())
    assert package_python_schedule.is_newer_than(min_date)

    # null list check
    package_python_schedule.packages["python-schedule"].build_date = None
    assert package_python_schedule.is_newer_than(min_date)

    package_python_schedule.packages["python2-schedule"].build_date = None
    assert not package_python_schedule.is_newer_than(min_date)


def test_is_outdated_false(package_ahriman: Package, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must be not outdated for the same package
    """
    actual_version_mock = mocker.patch("ahriman.models.package.Package.actual_version",
                                       return_value=package_ahriman.version)
    assert not package_ahriman.is_outdated(package_ahriman, configuration)
    actual_version_mock.assert_called_once_with(configuration)


def test_is_outdated_true(package_ahriman: Package, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must be outdated for the new version
    """
    other = Package.from_json(package_ahriman.view())
    other.version = other.version.replace("-1", "-2")
    actual_version_mock = mocker.patch("ahriman.models.package.Package.actual_version", return_value=other.version)

    assert package_ahriman.is_outdated(other, configuration)
    actual_version_mock.assert_called_once_with(configuration)


def test_is_outdated_no_version_calculation(package_ahriman: Package, configuration: Configuration,
                                            mocker: MockerFixture) -> None:
    """
    must not call actual version if calculation is disabled
    """
    actual_version_mock = mocker.patch("ahriman.models.package.Package.actual_version")
    assert not package_ahriman.is_outdated(package_ahriman, configuration, calculate_version=False)
    actual_version_mock.assert_not_called()


def test_is_outdated_fresh_package(package_ahriman: Package, configuration: Configuration,
                                   mocker: MockerFixture) -> None:
    """
    must not call actual version if package is never than specified time
    """
    configuration.set_option("build", "vcs_allowed_age", str(int(utcnow().timestamp())))
    actual_version_mock = mocker.patch("ahriman.models.package.Package.actual_version")
    assert not package_ahriman.is_outdated(package_ahriman, configuration)
    actual_version_mock.assert_not_called()


def test_next_pkgrel(package_ahriman: Package) -> None:
    """
    must correctly bump pkgrel
    """
    assert package_ahriman.next_pkgrel(package_ahriman.version) == "1.1"

    package_ahriman.version = "1.0.0-1.1"
    assert package_ahriman.next_pkgrel(package_ahriman.version) == "1.2"

    package_ahriman.version = "1.0.0-1.2.1"
    assert package_ahriman.next_pkgrel(package_ahriman.version) == "1.2.2"

    package_ahriman.version = "1:1.0.0-1"
    assert package_ahriman.next_pkgrel("1:1.0.1-1") == "1.1"
    assert package_ahriman.next_pkgrel("2:1.0.0-1") == "1.1"

    package_ahriman.version = "1.0.0-1.1"
    assert package_ahriman.next_pkgrel("1.0.1-2") == "2.1"
    assert package_ahriman.next_pkgrel("1.0.0-2") == "2.1"

    package_ahriman.version = "1.0.0-2"
    assert package_ahriman.next_pkgrel("1.0.0-1.1") is None

    assert package_ahriman.next_pkgrel(None) is None


def test_build_status_pretty_print(package_ahriman: Package) -> None:
    """
    must return string in pretty print function
    """
    assert package_ahriman.pretty_print()
    assert isinstance(package_ahriman.pretty_print(), str)


def test_with_packages(package_ahriman: Package, package_python_schedule: Package, pacman: Pacman,
                       mocker: MockerFixture) -> None:
    """
    must correctly replace packages descriptions
    """
    paths = [Path("1"), Path("2")]
    from_archive_mock = mocker.patch("ahriman.models.package.Package.from_archive", side_effect=[
        package_ahriman, package_python_schedule
    ])

    result = copy.deepcopy(package_ahriman)
    package_ahriman.packages[package_ahriman.base].architecture = "i686"

    result.with_packages(paths, pacman)
    from_archive_mock.assert_has_calls([
        MockCall(path, pacman) for path in paths
    ])
    assert result.packages[result.base] == package_ahriman.packages[package_ahriman.base]
