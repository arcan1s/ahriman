from distutils.util import convert_path
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
metadata = dict()
with open(convert_path("src/ahriman/version.py")) as metadata_file:
    exec(metadata_file.read(), metadata)

setup(
    name="ahriman",

    version=metadata["__version__"],
    zip_safe=False,

    description="ArcHlinux ReposItory MANager",

    author="arcanis",
    author_email="",
    url="https://github.com/arcan1s/ahriman",

    license="GPL3",

    packages=find_packages("src"),
    package_dir={"": "src"},

    dependency_links=[
    ],
    install_requires=[
        "aur",
        "pyalpm",
        "srcinfo",
    ],
    setup_requires=[
        "pytest-runner",
    ],
    tests_require=[
        "pytest",
        "pytest-aiohttp",
        "pytest-cov",
        "pytest-helpers-namespace",
        "pytest-mock",
        "pytest-pspec",
        "pytest-resource-path",
    ],

    include_package_data=True,
    scripts=[
        "package/bin/ahriman",
    ],
    data_files=[
        ("/etc", [
            "package/etc/ahriman.ini",
        ]),
        ("/etc/ahriman.ini.d", [
            "package/etc/ahriman.ini.d/logging.ini",
        ]),
        ("lib/systemd/system", [
            "package/lib/systemd/system/ahriman@.service",
            "package/lib/systemd/system/ahriman@.timer",
            "package/lib/systemd/system/ahriman-web@.service",
        ]),
        ("share/ahriman", [
            "package/share/ahriman/build-status.jinja2",
            "package/share/ahriman/repo-index.jinja2",
            "package/share/ahriman/search.jinja2",
            "package/share/ahriman/search-line.jinja2",
            "package/share/ahriman/sorttable.jinja2",
            "package/share/ahriman/style.jinja2",
        ]),
    ],

    extras_require={
        "check": [
            "autopep8",
            "mypy",
            "pylint",
        ],
        "test": [
            "pytest",
            "pytest-aiohttp",
            "pytest-cov",
            "pytest-helpers-namespace",
            "pytest-mock",
            "pytest-pspec",
            "pytest-resource-path",
        ],
        "web": [
            "Jinja2",
            "aiohttp",
            "aiohttp_jinja2",
            "requests",
        ],
    },
)
