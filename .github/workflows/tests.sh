#!/bin/bash
# Install dependencies and run test in container

set -ex

# install dependencies
pacman --noconfirm -Syyu base-devel python-tox

# run test and check targets
tox
