from pathlib import Path
from setuptools import find_packages, setup
from typing import Any, Dict


metadata_path = Path(__file__).resolve().parent / "src/ahriman/version.py"
metadata: Dict[str, Any] = {}
with metadata_path.open() as metadata_file:
    exec(metadata_file.read(), metadata)  # pylint: disable=exec-used


setup(
    name="ahriman",

    version=metadata["__version__"],
    zip_safe=False,

    description="ArcH linux ReposItory MANager",

    author="ahriman team",
    author_email="",
    url="https://github.com/arcan1s/ahriman",

    license="GPL3",

    packages=find_packages("src"),
    package_dir={"": "src"},

    dependency_links=[
    ],
    install_requires=[
        "inflection",
        "passlib",
        "requests",
        "setuptools",
        "srcinfo",
    ],
    setup_requires=[
    ],
    tests_require=[
        "pytest",
        "pytest-aiohttp",
        "pytest-cov",
        "pytest-helpers-namespace",
        "pytest-mock",
        "pytest-spec",
        "pytest-resource-path",
    ],

    include_package_data=True,
    scripts=[
        "package/bin/ahriman",
    ],
    data_files=[
        ("share/ahriman/settings", [
            "package/share/ahriman/settings/ahriman.ini",
        ]),
        ("share/ahriman/settings/ahriman.ini.d", [
            "package/share/ahriman/settings/ahriman.ini.d/logging.ini",
        ]),
        ("lib/systemd/system", [
            "package/lib/systemd/system/ahriman@.service",
            "package/lib/systemd/system/ahriman@.timer",
            "package/lib/systemd/system/ahriman-web@.service",
        ]),
        ("share/ahriman/templates", [
            "package/share/ahriman/templates/build-status.jinja2",
            "package/share/ahriman/templates/email-index.jinja2",
            "package/share/ahriman/templates/error.jinja2",
            "package/share/ahriman/templates/repo-index.jinja2",
            "package/share/ahriman/templates/shell",
            "package/share/ahriman/templates/telegram-index.jinja2",
        ]),
        ("share/ahriman/templates/build-status", [
            "package/share/ahriman/templates/build-status/failed-modal.jinja2",
            "package/share/ahriman/templates/build-status/key-import-modal.jinja2",
            "package/share/ahriman/templates/build-status/login-modal.jinja2",
            "package/share/ahriman/templates/build-status/package-add-modal.jinja2",
            "package/share/ahriman/templates/build-status/package-info-modal.jinja2",
            "package/share/ahriman/templates/build-status/package-rebuild-modal.jinja2",
            "package/share/ahriman/templates/build-status/success-modal.jinja2",
            "package/share/ahriman/templates/build-status/table.jinja2",
        ]),
        ("share/ahriman/templates/static", [
            "package/share/ahriman/templates/static/favicon.ico",
        ]),
        ("share/ahriman/templates/utils", [
            "package/share/ahriman/templates/utils/bootstrap-scripts.jinja2",
            "package/share/ahriman/templates/utils/style.jinja2",
        ]),
        ("share/man/man1", [
            "docs/ahriman.1",
        ])
    ],

    extras_require={
        "check": [
            "autopep8",
            "bandit",
            "mypy",
            "pylint",
        ],
        "docs": [
            "Sphinx",
            "argparse-manpage",
            "pydeps",
            "sphinx-argparse",
            "sphinxcontrib-napoleon",
        ],
        # FIXME technically this dependency is required, but in some cases we do not have access to
        # the libalpm which is required in order to install the package. Thus in case if we do not
        # really need to run the application we can move it to "optional" dependencies
        "pacman": [
            "pyalpm",
        ],
        "s3": [
            "boto3",
        ],
        "tests": [
            "pytest",
            "pytest-aiohttp",
            "pytest-cov",
            "pytest-helpers-namespace",
            "pytest-mock",
            "pytest-resource-path",
            "pytest-spec",
        ],
        "web": [
            "Jinja2",
            "aiohttp",
            "aiohttp_jinja2",
            "aioauth-client",
            "aiohttp_debugtoolbar",
            "aiohttp_session",
            "aiohttp_security",
            "cryptography",
            "requests-unixsocket",  # required by unix socket support
        ],
    },
)
