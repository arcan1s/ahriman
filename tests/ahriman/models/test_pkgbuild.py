import pytest

from io import BytesIO, StringIO
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
    open_mock.return_value.__enter__.return_value = BytesIO(b"content")
    load_mock = mocker.patch("ahriman.models.pkgbuild.Pkgbuild.from_io", return_value=pkgbuild_ahriman)

    assert Pkgbuild.from_file(Path("local"))
    open_mock.assert_called_once_with("rb")
    load_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_from_file_latin(pkgbuild_ahriman: Pkgbuild, mocker: MockerFixture) -> None:
    """
    must correctly load from file with latin encoding
    """
    open_mock = mocker.patch("pathlib.Path.open")
    open_mock.return_value.__enter__.return_value = BytesIO("contént".encode("latin-1"))
    load_mock = mocker.patch("ahriman.models.pkgbuild.Pkgbuild.from_io", return_value=pkgbuild_ahriman)

    assert Pkgbuild.from_file(Path("local"))
    open_mock.assert_called_once_with("rb")
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
    must correctly load package function
    """
    assert pkgbuild_ahriman.packages() == {pkgbuild_ahriman["pkgbase"]: Pkgbuild({})}


def test_packages_multi(resource_path_root: Path) -> None:
    """
    must correctly load list of package functions
    """
    pkgbuild = Pkgbuild.from_file(resource_path_root / "models" / "package_gcc10_pkgbuild")
    packages = pkgbuild.packages()

    assert all(pkgname in packages for pkgname in pkgbuild["pkgname"])
    assert all("pkgdesc" in package for package in packages.values())
    assert all("depends" in package for package in packages.values())


def test_packages_empty(pkgbuild_ahriman: Pkgbuild) -> None:
    """
    must correctly load packages without package functionn
    """
    del pkgbuild_ahriman.fields["package()"]
    assert pkgbuild_ahriman.packages() == {pkgbuild_ahriman["pkgbase"]: Pkgbuild({})}


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


def test_parse_ahriman(resource_path_root: Path) -> None:
    """
    must parse real PKGBUILDs correctly (ahriman)
    """
    pkgbuild = Pkgbuild.from_file(resource_path_root / "models" / "package_ahriman_pkgbuild")
    values = {key: value.value for key, value in pkgbuild.fields.items() if not value.is_function}
    assert values == {
        "pkgbase": "ahriman",
        "pkgname": "ahriman",
        "pkgver": "2.6.0",
        "pkgrel": "1",
        "pkgdesc": "ArcH linux ReposItory MANager",
        "arch": ["any"],
        "url": "https://github.com/arcan1s/ahriman",
        "license": ["GPL3"],
        "depends": [
            "devtools",
            "git",
            "pyalpm",
            "python-cerberus",
            "python-inflection",
            "python-passlib",
            "python-requests",
            "python-setuptools",
            "python-srcinfo",
        ],
        "makedepends": [
            "python-build",
            "python-installer",
            "python-wheel",
        ],
        "optdepends": [
            "breezy: -bzr packages support",
            "darcs: -darcs packages support",
            "mercurial: -hg packages support",
            "python-aioauth-client: web server with OAuth2 authorization",
            "python-aiohttp: web server",
            "python-aiohttp-debugtoolbar: web server with enabled debug panel",
            "python-aiohttp-jinja2: web server",
            "python-aiohttp-security: web server with authorization",
            "python-aiohttp-session: web server with authorization",
            "python-boto3: sync to s3",
            "python-cryptography: web server with authorization",
            "python-requests-unixsocket: client report to web server by unix socket",
            "python-jinja: html report generation",
            "rsync: sync by using rsync",
            "subversion: -svn packages support",
        ],
        "source": [
            "https://github.com/arcan1s/ahriman/releases/download/$pkgver/$pkgname-$pkgver-src.tar.xz",
            "ahriman.sysusers",
            "ahriman.tmpfiles",
        ],
        "backup": [
            "etc/ahriman.ini",
            "etc/ahriman.ini.d/logging.ini",
        ],
        "sha512sums": [
            "ec1f64e463455761d72be7f7b8b51b3b4424685c96a2d5eee6afa1c93780c8d7f8a39487a2f2f3bd83d2b58a93279e1392a965a4b905795e58ca686fb21123a1",
            "53d37efec812afebf86281716259f9ea78a307b83897166c72777251c3eebcb587ecee375d907514781fb2a5c808cbb24ef9f3f244f12740155d0603bf213131",
            "62b2eccc352d33853ef243c9cddd63663014aa97b87242f1b5bc5099a7dbd69ff3821f24ffc58e1b7f2387bd4e9e9712cc4c67f661b1724ad99cdf09b3717794",
        ],
    }


def test_parse_gcc10(resource_path_root: Path) -> None:
    """
    must parse real PKGBUILDs correctly (gcc10)
    """
    pkgbuild = Pkgbuild.from_file(resource_path_root / "models" / "package_gcc10_pkgbuild")
    values = {key: value.value for key, value in pkgbuild.fields.items() if not value.is_function}
    assert values == {
        "pkgbase": "gcc10",
        "pkgname": [
            "${pkgbase}",
            "${pkgbase}-libs",
            "${pkgbase}-fortran",
        ],
        "pkgver": "10.5.0",
        "_majorver": "${pkgver%%.*}",
        "_islver": "0.24",
        "pkgrel": "2",
        "pkgdesc": "The GNU Compiler Collection (10.x.x)",
        "arch": ["x86_64"],
        "url": "https://gcc.gnu.org",
        "license": [
            "GPL-3.0-or-later",
            "LGPL-3.0+",
            "GFDL-1.3",
            "LicenseRef-custom",
        ],
        "makedepends": [
            "binutils",
            "doxygen",
            "git",
            "libmpc",
            "python",
        ],
        "checkdepends": [
            "dejagnu",
            "inetutils",
        ],
        "options": [
            "!emptydirs",
            "!lto",
            "!buildflags",
        ],
        "source": [
            "https://sourceware.org/pub/gcc/releases/gcc-${pkgver}/gcc-${pkgver}.tar.xz",
            "https://sourceware.org/pub/gcc/releases/gcc-${pkgver}/gcc-${pkgver}.tar.xz.sig",
            "https://sourceware.org/pub/gcc/infrastructure/isl-${_islver}.tar.bz2",
            "c89",
            "c99",
        ],
        "validpgpkeys": [
            "F3691687D867B81B51CE07D9BBE43771487328A9",
            "86CFFCA918CF3AF47147588051E8B148A9999C34",
            "13975A70E63C361C73AE69EF6EEB81F8981C74C7",
            "D3A93CAD751C2AF4F8C7AD516C35B99309B5FA62",
        ],
        "md5sums": [
            "c7d1958570fbd1cd859b015774b9987a",
            "SKIP",
            "dd2f7b78e118c25bd96134a52aae7f4d",
            "d5fd2672deb5f97a2c4bdab486470abe",
            "d99ba9f4bd860e274f17040ee51cd1bf",
        ],
        "b2sums": [
            "9b71761f4015649514677784443886e59733ac3845f7dfaa4343f46327d36c08c403c444b9e492b870ac0b3f2e3568f972b7700a0ef05a497fb4066079b3143b",
            "SKIP",
            "88a178dad5fe9c33be5ec5fe4ac9abc0e075a86cff9184f75cedb7c47de67ce3be273bd0db72286ba0382f4016e9d74855ead798ad7bccb015b853931731828e",
            "a76d19c7830b0a141302890522086fc1548c177611501caac7e66d576e541b64ca3f6e977de715268a9872dfdd6368a011b92e01f7944ec0088f899ac0d2a2a5",
            "02b655b5668f7dea51c3b3e4ff46d5a4aee5a04ed5e26b98a6470f39c2e98ddc0519bffeeedd982c31ef3c171457e4d1beaff32767d1aedd9346837aac4ec3ee",
        ],
        "_CHOST": "${CHOST:=}",
        "_MAKEFLAGS": "${MAKEFLAGS:=}",
        "_libdir": "usr/lib/gcc/${CHOST}/${pkgver%%+*}",
    }


def test_parse_jellyfin_ffmpeg6_bin(resource_path_root: Path) -> None:
    """
    must parse real PKGBUILDs correctly (jellyfin-ffmpeg6-bin)
    """
    pkgbuild = Pkgbuild.from_file(resource_path_root / "models" / "package_jellyfin-ffmpeg6-bin_pkgbuild")
    values = {key: value.value for key, value in pkgbuild.fields.items() if not value.is_function}
    assert values == {
        "pkgbase": "jellyfin-ffmpeg6-bin",
        "pkgname": "jellyfin-ffmpeg6-bin",
        "pkgver": "6.0",
        "pkgrel": "6",
        "pkgdesc": "FFmpeg6 binary version for Jellyfin",
        "arch": ["x86_64", "aarch64"],
        "url": "https://github.com/jellyfin/jellyfin-ffmpeg",
        "license": ["GPL3"],
        "depends_x86_64": ["glibc>=2.23"],
        "depends_aarch64": ["glibc>=2.27"],
        "optdepends": [
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
        "conflicts": [
            "jellyfin-ffmpeg",
            "jellyfin-ffmpeg5",
            "jellyfin-ffmpeg5-bin",
            "jellyfin-ffmpeg6",
        ],
        "source_x86_64": ["https://repo.jellyfin.org/releases/ffmpeg/${pkgver}-${pkgrel}/jellyfin-ffmpeg_${pkgver}-${pkgrel}_portable_linux64-gpl.tar.xz"],
        "source_aarch64": ["https://repo.jellyfin.org/releases/ffmpeg/${pkgver}-${pkgrel}/jellyfin-ffmpeg_${pkgver}-${pkgrel}_portable_linuxarm64-gpl.tar.xz"],
        "sha256sums_x86_64": ["32cbe40942d26072faa1182835ccc89029883766de11778c731b529aa632ff37"],
        "sha256sums_aarch64": ["22b8f2a3c92c6b1c9e6830a6631f08f3f0a7ae80739ace71ad30704a28045184"],
    }


def test_parse_tpacpi_bat_git(resource_path_root: Path) -> None:
    """
    must parse real PKGBUILDs correctly (tpacpi-bat-git)
    """
    pkgbuild = Pkgbuild.from_file(resource_path_root / "models" / "package_tpacpi-bat-git_pkgbuild")
    values = {key: value.value for key, value in pkgbuild.fields.items() if not value.is_function}
    assert values == {
        "pkgbase": "tpacpi-bat-git",
        "pkgname": "tpacpi-bat-git",
        "pkgver": "3.1.r13.g4959b52",
        "pkgrel": "1",
        "pkgdesc": "A Perl script with ACPI calls for recent ThinkPads which are not supported by tp_smapi",
        "arch": ["any"],
        "url": "https://github.com/teleshoes/tpacpi-bat",
        "license": ["GPL3"],
        "depends": ["perl", "acpi_call"],
        "makedepends": ["git"],
        "provides": ["tpacpi-bat"],
        "conflicts": ["tpacpi-bat"],
        "backup": ["etc/conf.d/tpacpi"],
        "source": ["git+https://github.com/teleshoes/tpacpi-bat.git"],
        "b2sums": ["SKIP"],
    }


def test_parse_yay(resource_path_root: Path) -> None:
    """
    must parse real PKGBUILDs correctly (yay)
    """
    pkgbuild = Pkgbuild.from_file(resource_path_root / "models" / "package_yay_pkgbuild")
    values = {key: value.value for key, value in pkgbuild.fields.items() if not value.is_function}
    assert values == {
        "pkgbase": "yay",
        "pkgname": "yay",
        "pkgver": "12.3.5",
        "pkgrel": "1",
        "pkgdesc": "Yet another yogurt. Pacman wrapper and AUR helper written in go.",
        "arch": [
            "i686",
            "pentium4",
            "x86_64",
            "arm",
            "armv7h",
            "armv6h",
            "aarch64",
            "riscv64",
        ],
        "url": "https://github.com/Jguer/yay",
        "options": ["!lto"],
        "license": ["GPL-3.0-or-later"],
        "depends": [
            "pacman>6.1",
            "git",
        ],
        "optdepends": [
            "sudo: privilege elevation",
            "doas: privilege elevation",
        ],
        "makedepends": ["go>=1.21"],
        "source": ["${pkgname}-${pkgver}.tar.gz::https://github.com/Jguer/yay/archive/v${pkgver}.tar.gz"],
        "sha256sums": ["2fb6121a6eb4c5e6afaf22212b2ed15022500a4bc34bb3dc0f9782c1d43c3962"],
    }


def test_parse_vim_youcompleteme_git(resource_path_root: Path) -> None:
    """
    must parse real PKGBUILDs correctly (vim-youcompleteme-git)
    """
    pkgbuild = Pkgbuild.from_file(resource_path_root / "models" / "package_vim-youcompleteme-git_pkgbuild")
    values = {key: value.value for key, value in pkgbuild.fields.items() if not value.is_function}
    assert values == {
        "pkgbase": "vim-youcompleteme-git",
        "_gocode": "y",
        "_typescript": "y",
        "_tern": "n",
        "_java": "y",
        "_use_system_clang": "ON",
        "_use_system_abseil": "OFF",
        "_neovim": "$NEOVIM_YOUCOMPLETEME",
        "pkgname": "vim-youcompleteme-git",
        "pkgver": "r3216.0d855962",
        "pkgrel": "1",
        "pkgdesc": "A code-completion engine for Vim",
        "arch": ["x86_64"],
        "url": "https://ycm-core.github.io/YouCompleteMe/",
        "license": ["GPL3"],
        "groups": ["vim-plugins"],
        "depends": [
            "vim",
            "python>=3.6",
            "python-watchdog",
            "python-bottle",
            "clang"
        ],
        "makedepends": [
            "git",
            "cmake",
            "pybind11",
        ],
        "optdepends": [
            "gopls: Go semantic completion",
            "nodejs-tern: JavaScript semantic completion",
            "rust-analyzer: Rust semantic completion",
            "typescript: Typescript semantic completion",
            "python-jedi: Python semantic completion",
            "python-numpydoc: Python semantic completion",
            "python-regex: Better Unicode support",
            "omnisharp-roslyn: C# semantic completion",
            "java-environment>=11: Java semantic completion",
            "jdtls: Java semantic completion",
            "abseil-cpp: if setting _use_system_abseil ON",
        ],
        "source": [
            "git+https://github.com/ycm-core/YouCompleteMe.git",
            "git+https://github.com/ycm-core/ycmd.git",
            "clangd-15.0.1.tar.bz2::https://github.com/ycm-core/llvm/releases/download/15.0.1/clangd-15.0.1-x86_64-unknown-linux-gnu.tar.bz2",
            "libclang-15.0.1.tar.bz2::https://github.com/ycm-core/llvm/releases/download/15.0.1/libclang-15.0.1-x86_64-unknown-linux-gnu.tar.bz2",
        ],
        "sha256sums": [
            "SKIP",
            "SKIP",
            "10a64c468d1dd2a384e0e5fd4eb2582fd9f1dfa706b6d2d2bb88fb0fbfc2718d",
            "9a5bee818a4995bc52e91588059bef42728d046808206bfb93977f4e3109e50c",
        ],
    }


def test_parse_python_pytest_loop(resource_path_root: Path) -> None:
    """
    must parse real PKGBUILDs correctly (python-pytest-loop)
    """
    pkgbuild = Pkgbuild.from_file(resource_path_root / "models" / "package_python-pytest-loop_pkgbuild")
    values = {key: value.value for key, value in pkgbuild.fields.items() if not value.is_function}
    assert values == {
        "pkgbase": "python-pytest-loop",
        "_pname": "${pkgbase#python-}",
        "_pyname": "${_pname//-/_}",
        "pkgname": ["python-${_pname}"],
        "pkgver": "1.0.13",
        "pkgrel": "1",
        "pkgdesc": "Pytest plugin for looping test execution.",
        "arch": ["any"],
        "url": "https://github.com/anogowski/pytest-loop",
        "license": ["MPL-2.0"],
        "makedepends": [
            "python-hatchling",
            "python-versioningit",
            "python-wheel",
            "python-build",
            "python-installer",
        ],
        "checkdepends": [
            "python-pytest",
        ],
        "source": [
            "https://files.pythonhosted.org/packages/source/${_pyname:0:1}/${_pyname}/${_pyname}-${pkgver}.tar.gz",
        ],
        "md5sums": [
            "98365f49606d5068f92350f1d2569a5f",
        ],
    }


def test_parse_pacman_static(resource_path_root: Path) -> None:
    """
    must parse real PKGBUILDs correctly (pacman-static)
    """
    pkgbuild = Pkgbuild.from_file(resource_path_root / "models" / "package_pacman-static_pkgbuild")
    values = {key: value.value for key, value in pkgbuild.fields.items() if not value.is_function}
    print(values)
    assert values == {
        "pkgbase": "pacman-static",
        "pkgname": "pacman-static",
        "pkgver": "7.0.0.r6.gc685ae6",
        "_cares_ver": "1.34.4",
        "_nghttp2_ver": "1.64.0",
        "_curlver": "8.12.1",
        "_sslver": "3.4.1",
        "_zlibver": "1.3.1",
        "_xzver": "5.6.4",
        "_bzipver": "1.0.8",
        "_zstdver": "1.5.6",
        "_libarchive_ver": "3.7.7",
        "_gpgerrorver": "1.51",
        "_libassuanver": "3.0.0",
        "_gpgmever": "1.24.2",
        "pkgrel": "15",
        "_git_tag": "7.0.0",
        "_git_patch_level_commit": "c685ae6412af04cae1eaa5d6bda8c277c7ffb8c8",
        "pkgdesc": "Statically-compiled pacman (to fix or install systems without libc)",
        "arch": [
            "i486",
            "i686",
            "pentium4",
            "x86_64",
            "arm",
            "armv6h",
            "armv7h",
            "aarch64"
        ],
        "url": "https://www.archlinux.org/pacman/",
        "license": ["GPL-2.0-or-later"],
        "depends": ["pacman"],
        "makedepends": [
            "meson",
            "musl",
            "kernel-headers-musl",
            "git",
        ],
        "options": [
            "!emptydirs",
            "!lto",
        ],
        "source": [
            "git+https://gitlab.archlinux.org/pacman/pacman.git#tag=v${_git_tag}?signed",
            "pacman-revertme-makepkg-remove-libdepends-and-libprovides.patch::https://gitlab.archlinux.org/pacman/pacman/-/commit/354a300cd26bb1c7e6551473596be5ecced921de.patch",
        ],
        "validpgpkeys": [
            "6645B0A8C7005E78DB1D7864F99FFE0FEAE999BD",
            "B8151B117037781095514CA7BBDFFC92306B1121",
        ],
        "sha512sums": [
            "44e00c2bc259fe6a85de71f7fd8a43fcfd1b8fb7d920d2267bd5b347e02f1dab736b3d96e31faf7b535480398e2348f7c0b9914e51ca7e12bab2d5b8003926b4",
            "1a108c4384b6104e627652488659de0b1ac3330640fc3250f0a283af7c5884daab187c1efc024b2545262da1911d2b0b7b0d5e4e5b68bb98db25a760c9f1fb1a",
            "b544196c3b7a55faacd11700d11e2fe4f16a7418282c9abb24a668544a15293580fd1a2cc5f93367c8a17c7ee45335c6d2f5c68a72dd176d516fd033f203eeec",
            "3285e14d94bc736d6caddfe7ad7e3c6a6e69d49b079c989bb3e8aba4da62c022e38229d1e691aaa030b7d3bcd89e458d203f260806149a71ad9adb31606eae02",
            "SKIP",
            "9fcdcceab8bce43e888db79a38c775ff15790a806d3cc5cc96f396a829c6da2383b258481b5642153da14087943f6ef607af0aa3b75df6f41b95c6cd61d835eb",
            "SKIP",
            "1de6307c587686711f05d1e96731c43526fa3af51e4cd94c06c880954b67f6eb4c7db3177f0ea5937d41bc1f8cadcf5bce75025b5c1a46a469376960f1001c5f",
            "SKIP",
            "b1873dbb7a49460b007255689102062756972de5cc2d38b12cc9f389b6be412da6797579b1acd3717a8cd2ee118fd9801b94e55f063d4328f050f0876a5eb53c",
            "b5887ea77417fae49b6cb1e9fa782d3021f268d5219701d87a092235964f73fa72a31428b630445517f56f2bb69dcbbb24119ef9dbf8b4e40a753369a9f9a16f",
            "580677aad97093829090d4b605ac81c50327e74a6c2de0b85dd2e8525553f3ddde17556ea46f8f007f89e435493c9a20bc997d1ef1c1c2c23274528e3c46b94f",
            "SKIP",
            "e3216eca5fae2c9ce419e698bfbe186903088dad0a579749cb49bcde8f9d4073b98bf1570fe69190a9a41feb2a7c9814498ec9b867527de1c74ff75a1cbdfc17",
            "083f5e675d73f3233c7930ebe20425a533feedeaaa9d8cc86831312a6581cefbe6ed0d08d2fa89be81082f2a5abdabca8b3c080bf97218a1bd59dc118a30b9f3",
            "SKIP",
            "21f9da445afd76acaf3acb22d216c2b584d95e8c68e00f5cb3f6673f2d556dd14a7593344adf8ffd194bba3314387ee0e486d6248f6c935abca2edd8a4cf95ed",
            "SKIP",
            "4489f615c6a0389577a7d1fd7d3917517bb2fe032abd9a6d87dfdbd165dabcf53f8780645934020bf27517b67a064297475888d5b368176cf06bc22f1e735e2b",
            "SKIP",
            "7c5c95c1b85bef2d4890c068a5a8ea8a1fe0d8def6ab09e5f34fc2746d8808bbb0fc168e3bd66d52ee5ed799dcf9f258f4125cda98c8384f6411bcad8d8b3139",
            "SKIP",
            "ad69101d1fceef6cd1dd6d5348f6f2be06912da6b6a7d0fece3ce08cf35054e6953b80ca9c4748554882892faa44e7c54e705cf25bbf2b796cd4ad12b09da185",
            "SKIP",
            "2524f71f4c2ebc254a1927279be3394e820d0a0c6dec7ef835a862aa08c35756edaa4208bcdc710dd092872b59c200b555b78670372e2830822e278ff1ec4e4a",
            "SKIP",
        ],
        "LDFLAGS": "$LDFLAGS -static",
        "CC": "musl-gcc -fno-stack-protector",
        "CXX": "musl-gcc -fno-stack-protector",
        "CFLAGS": "${CFLAGS/-fstack-protector-strong/}",
        "CXXFLAGS": "${CXXFLAGS/-fstack-protector-strong/}",
        "PKGEXT": ".pkg.tar.xz",
    }
