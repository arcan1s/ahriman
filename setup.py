from distutils.util import convert_path
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
metadata = dict()
with open(convert_path('src/ahriman/version.py')) as metadata_file:
    exec(metadata_file.read(), metadata)

setup(
    name='ahriman',

    version=metadata['__version__'],
    zip_safe=False,

    description='ArcHlinux ReposItory MANager',

    author='arcanis',
    author_email='',
    url='',

    license='GPL3',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    dependency_links=[
    ],
    install_requires=[
        'aur',
        'srcinfo',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],

    include_package_data=True,
    scripts=[
        'package/bin/ahriman'
    ],
    data_files=[
        ('/etc', ['package/etc/ahriman.ini']),
        ('/etc/ahriman.ini.d', ['package/etc/ahriman.ini.d/logging.ini']),
        ('lib/systemd/system', [
            'package/lib/systemd/system/ahriman.service',
            'package/lib/systemd/system/ahriman.timer'
        ])
    ],

    extras_require={
        'test': ['coverage', 'pytest'],
    },
)
