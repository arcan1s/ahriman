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
    open_mock.assert_called_once_with(encoding="utf8")
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
