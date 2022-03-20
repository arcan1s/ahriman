#!/bin/bash
# Install dependencies and run test in container

set -ex

# install dependencies
pacman --noconfirm -Syu base-devel python-pip python-tox

# run test and check targets
make check tests
