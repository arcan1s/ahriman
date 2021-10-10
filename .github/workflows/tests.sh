#!/bin/bash
# Install dependencies and run test in container

set -ex

# install dependencies
pacman --noconfirm -Syu base-devel python-pip

# install python packages
pip install -e .[web]
pip install -e .[check]
pip install -e .[s3]
pip install -e .[test]

# run test and check targets
make check tests
